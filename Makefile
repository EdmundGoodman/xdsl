MAKEFLAGS += --no-builtin-rules
MAKEFLAGS += --no-builtin-variables

# use a default prefix for coverage data files
COVERAGE_FILE ?= .coverage

# allow overriding which extras are installed
VENV_EXTRAS ?= --extra gui --extra dev

# use different coverage data file per coverage run, otherwise combine complains
TESTS_COVERAGE_FILE = ${COVERAGE_FILE}.tests

# make tasks run all commands in a single shell
.ONESHELL:

.PHONY: uv-installed
uv-installed:
	@command -v uv &> /dev/null ||\
		(echo "UV doesn't seem to be installed, try the following instructions:" &&\
		echo "https://docs.astral.sh/uv/getting-started/installation/" && false)

# set up the venv with all dependencies for development
.venv/: uv-installed
	uv sync ${VENV_EXTRAS}

# make sure `make venv` also works correctly
.PHONY: venv
venv: .venv/

# remove all caches
.PHONY: clean-caches
clean-caches:
	rm -rf .pytest_cache *.egg-info .coverage.*
	find . -type f -name "*.cover" -delete

# remove all caches and the venv
.PHONY: clean
clean: clean-caches
	rm -rf ${VENV_DIR}

# run filecheck tests
.PHONY: filecheck
filecheck: uv-installed
	uv run lit -vv tests/filecheck --order=smart --timeout=20

# run pytest tests
.PHONY: pytest
pytest: uv-installed
	uv run pytest tests -W error -vv

# run pytest on notebooks
.PHONY: pytest-nb
pytest-nb: uv-installed
	uv run pytest -W error --nbval -vv docs \
		--ignore=docs/mlir_interoperation.ipynb \
		--nbval-current-env

# run tests for Toy tutorial
.PHONY: filecheck-toy
filecheck-toy: uv-installed
	uv run lit -v docs/Toy/examples --order=smart

.PHONY: pytest-toy
pytest-toy: uv-installed
	uv run pytest docs/Toy/toy/tests

.PHONY: tests-toy
tests-toy: filecheck-toy pytest-toy

.PHONY: tests-marimo
tests-marimo: uv-installed
	@for file in docs/marimo/*.py; do \
		echo "Running $$file"; \
		error_message=$$(uv run python3 "$$file" 2>&1) || { \
			echo "Error running $$file"; \
			echo "$$error_message"; \
			exit 1; \
		}; \
	done
	@echo "All marimo tests passed successfully."

.PHONY: tests-marimo-mlir
tests-marimo-mlir: uv-installed
	@if ! command -v mlir-opt > /dev/null 2>&1; then \
		echo "MLIR is not installed, skipping tests."; \
		exit 0; \
	fi
	@echo "MLIR is installed, running tests."
	@for file in docs/marimo/mlir/*.py; do \
		echo "Running $$file"; \
		error_message=$$(uv run python3 "$$file" 2>&1) || { \
			echo "Error running $$file"; \
			echo "$$error_message"; \
			exit 1; \
		}; \
	done
	@echo "All marimo mlir tests passed successfully."

# run all tests
.PHONY: tests
tests: pytest tests-toy filecheck pytest-nb tests-marimo tests-marimo-mlir pyright
	@echo All tests done.

# re-generate the output from all jupyter notebooks in the docs directory
.PHONY: rerun-notebooks
rerun-notebooks: uv-installed
	uv run jupyter nbconvert \
		--ClearMetadataPreprocessor.enabled=True \
		--inplace \
		--to notebook \
		--execute docs/*.ipynb docs/Toy/*.ipynb

# set up all precommit hooks
.PHONY: precommit-install
precommit-install: uv-installed
	uv run pre-commit install

# run all precommit hooks and apply them
.PHONY: precommit
precommit: uv-installed
	uv run pre-commit run --all

# run pyright on all files in the current git commit
.PHONY: pyright
pyright: uv-installed
    # We make sure to generate the python typing stubs before running pyright
	uv run xdsl-stubgen
	uv run pyright $(shell git diff --staged --name-only  -- '*.py')

# run coverage over all tests and combine data files
.PHONY: coverage
coverage: uv-installed coverage-tests coverage-filecheck-tests
	uv run coverage combine --append

# run coverage over tests
.PHONY: coverage-tests
coverage-tests: uv-installed
	COVERAGE_FILE=${TESTS_COVERAGE_FILE} uv run pytest -W error --cov --cov-config=.coveragerc

# run coverage over filecheck tests
.PHONY: coverage-filecheck-tests
coverage-filecheck-tests: uv-installed
	uv run lit -v tests/filecheck/ -DCOVERAGE

# generate html coverage report
.PHONY: coverage-report-html
coverage-report-html: uv-installed
	uv run coverage html

# generate markdown coverage report
.PHONY: coverage-report-html
coverage-report-md: uv-installed
	uv run coverage report --format=markdown
