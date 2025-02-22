#!/usr/bin/env python3
"""Benchmark running xDSL opt end-to-end on MLIR files."""

from pathlib import Path

from xdsl.xdsl_opt_main import xDSLOptMain

BENCHMARKS_DIR = Path(__file__).parent
EXTRA_MLIR_DIR = BENCHMARKS_DIR / "resources" / "extra_mlir"


class ConstantFolding:
    """Benchmark running `xdsl-opt` on constant folding workloads."""

    WORKLOAD_4 = str(EXTRA_MLIR_DIR / "constant_folding_4.mlir")
    WORKLOAD_20 = str(EXTRA_MLIR_DIR / "constant_folding_20.mlir")
    WORKLOAD_100 = str(EXTRA_MLIR_DIR / "constant_folding_100.mlir")
    WORKLOAD_1000 = str(EXTRA_MLIR_DIR / "constant_folding_1000.mlir")

    def ignore_time_4(self) -> None:
        """Time constant folding for 4 items."""
        xDSLOptMain(
            args=[ConstantFolding.WORKLOAD_4, "-p", "constant-fold-interp"]
        ).run()  # type: ignore[no-untyped-call]

    def ignore_time_20(self) -> None:
        """Time constant folding for 20 items."""
        xDSLOptMain(
            args=[ConstantFolding.WORKLOAD_20, "-p", "constant-fold-interp"]
        ).run()  # type: ignore[no-untyped-call]

    def time_100(self) -> None:
        """Time constant folding for 100 items."""
        xDSLOptMain(
            args=[ConstantFolding.WORKLOAD_100, "-p", "constant-fold-interp"]
        ).run()  # type: ignore[no-untyped-call]

    def time_100_unverified(self) -> None:
        """Time constant folding for 100 items without the verifier."""
        xDSLOptMain(
            args=[
                ConstantFolding.WORKLOAD_100,
                "-p",
                "constant-fold-interp",
                "--disable-verify",
            ]
        ).run()  # type: ignore[no-untyped-call]

    def time_100_canonicalize(self) -> None:
        """Time canonicalizing constant folding for 100 items."""
        xDSLOptMain(args=[ConstantFolding.WORKLOAD_100, "-p", "canonicalize"]).run()  # type: ignore[no-untyped-call]

    def time_100_none(self) -> None:
        """Time applying no optimisations for 100 items."""
        xDSLOptMain(args=[ConstantFolding.WORKLOAD_100]).run()  # type: ignore[no-untyped-call]

    def ignore_time_1000(self) -> None:
        """Time constant folding for 1000 items."""
        xDSLOptMain(
            args=[ConstantFolding.WORKLOAD_1000, "-p", "constant-fold-interp"]
        ).run()  # type: ignore[no-untyped-call]


class Miscellaneous:
    """Benchmark running `xdsl-opt` on miscellaneous workloads."""

    WORKLOAD_EMPTY = str(EXTRA_MLIR_DIR / "xdsl_opt__empty_program.mlir")
    WORKLOAD_LARGE_DENSE_ATTR = str(EXTRA_MLIR_DIR / "large_dense_attr.mlir")
    WORKLOAD_LARGE_DENSE_ATTR_HEX = str(EXTRA_MLIR_DIR / "large_dense_attr_hex.mlir")

    def time_empty_program(self) -> None:
        """Time running the empty program."""
        xDSLOptMain(
            args=[
                Miscellaneous.WORKLOAD_EMPTY,
                "-p",
                "canonicalize",
            ]
        ).run()  # type: ignore[no-untyped-call]

    def ignore_time_dense_attr(self) -> None:
        """Time running a 1024x1024xi8 dense attribute."""
        xDSLOptMain(
            args=[
                Miscellaneous.WORKLOAD_LARGE_DENSE_ATTR,
                "-p",
                "canonicalize",
            ]
        ).run()  # type: ignore[no-untyped-call]

    def ignore_time_dense_attr_hex(self) -> None:
        """Time running a 1024x1024xi8 dense attribute given as a hex string."""
        xDSLOptMain(
            args=[
                Miscellaneous.WORKLOAD_LARGE_DENSE_ATTR_HEX,
                "-p",
                "canonicalize",
            ]
        ).run()  # type: ignore[no-untyped-call]


class CIRCT:
    """Benchmark running `xdsl-opt` on CIRCT workloads."""

    ...


class ASL:
    """Benchmark running `xdsl-opt` on ASL workloads."""

    ...


if __name__ == "__main__":
    from bench_utils import profile  # type: ignore

    CONSTANT_FOLDING = ConstantFolding()
    MISCELLANEOUS = Miscellaneous()

    BENCHMARKS = {
        "ConstantFolding.4": CONSTANT_FOLDING.ignore_time_4,
        "ConstantFolding.20": CONSTANT_FOLDING.ignore_time_20,
        "ConstantFolding.100": CONSTANT_FOLDING.time_100,
        "ConstantFolding.100_unverified": CONSTANT_FOLDING.time_100_unverified,
        "ConstantFolding.100_canonicalize": CONSTANT_FOLDING.time_100_canonicalize,
        "ConstantFolding.100_none": CONSTANT_FOLDING.time_100_none,
        "ConstantFolding.1000": CONSTANT_FOLDING.ignore_time_1000,
        "Miscellaneous.empty_program": MISCELLANEOUS.time_empty_program,
        "Miscellaneous.dense_attr": MISCELLANEOUS.ignore_time_dense_attr,
        "Miscellaneous.dense_attr_hex": MISCELLANEOUS.ignore_time_dense_attr_hex,
    }
    profile(BENCHMARKS)
