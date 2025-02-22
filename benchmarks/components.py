#!/usr/bin/env python3
"""Benchmarks for the pipeline stages of the xDSL implementation."""

from io import StringIO
from pathlib import Path

from xdsl.context import Context
from xdsl.dialects.builtin import ModuleOp
from xdsl.ir import Operation
from xdsl.parser import Parser as XdslParser
from xdsl.printer import Printer
from xdsl.transforms.canonicalize import CanonicalizePass
from xdsl.transforms.constant_fold_interp import ConstantFoldInterpPass
from xdsl.utils.lexer import Input
from xdsl.utils.mlir_lexer import MLIRLexer, MLIRTokenKind

CTX = Context(allow_unregistered=True)
PRINT_STREAM = StringIO()

BENCHMARKS_DIR = Path(__file__).parent
EXTRA_MLIR_DIR = BENCHMARKS_DIR / "resources" / "extra_mlir"


class Component:
    """Parent class containing workload paths."""

    WORKLOAD_EMPTY = EXTRA_MLIR_DIR / "xdsl_opt__empty_program.mlir"
    WORKLOAD_CONSTANT_100 = EXTRA_MLIR_DIR / "constant_folding_100.mlir"
    WORKLOAD_CONSTANT_1000 = EXTRA_MLIR_DIR / "constant_folding_1000.mlir"
    WORKLOAD_LARGE_DENSE_ATTR = EXTRA_MLIR_DIR / "large_dense_attr.mlir"
    WORKLOAD_LARGE_DENSE_ATTR_HEX = EXTRA_MLIR_DIR / "large_dense_attr_hex.mlir"

    @classmethod
    def lex_file(cls, mlir_file: Path) -> None:
        """Lex a mlir file."""
        contents = mlir_file.read_text()
        lexer_input = Input(contents, str(mlir_file))
        lexer = MLIRLexer(lexer_input)
        while lexer.lex().kind is not MLIRTokenKind.EOF:
            pass

    @classmethod
    def parse_operation(cls, mlir_file: Path) -> Operation:
        """Parse a MLIR file as an operation."""
        contents = mlir_file.read_text()
        parser = XdslParser(CTX, contents)
        return parser.parse_op()

    @classmethod
    def parse_module(cls, mlir_file: Path) -> ModuleOp:
        """Parse a MLIR file as a module."""
        contents = mlir_file.read_text()
        parser = XdslParser(CTX, contents)
        return parser.parse_module()

    @classmethod
    def constant_fold_module(cls, module: ModuleOp) -> ModuleOp:
        """Apply the constant folding pattern rewriter to a module."""
        ConstantFoldInterpPass().apply(CTX, module)
        return module

    @classmethod
    def canonicalize_module(cls, module: ModuleOp) -> ModuleOp:
        """Apply the canonicalization pattern rewriter to a module."""
        CanonicalizePass().apply(CTX, module)
        return module

    @classmethod
    def verify_module(cls, module: ModuleOp) -> None:
        """Verify a module."""
        module.verify()

    @classmethod
    def print_module(cls, module: ModuleOp) -> None:
        """Print a module."""
        Printer(stream=PRINT_STREAM).print_op(module)


class LexPhase(Component):
    """Benchmark the xDSL lexer on MLIR files."""

    def time_empty_program(self) -> None:
        """Time lexing an empty program."""
        Component.lex_file(Component.WORKLOAD_EMPTY)

    def time_constant_100(self) -> None:
        """Time lexing constant folding for 100 items."""
        Component.lex_file(Component.WORKLOAD_CONSTANT_100)

    def time_constant_1000(self) -> None:
        """Time lexing constant folding for 1000 items."""
        Component.lex_file(Component.WORKLOAD_CONSTANT_1000)

    def ignore_time_dense_attr(self) -> None:
        """Time lexing a 1024x1024xi8 dense attribute."""
        Component.lex_file(Component.WORKLOAD_LARGE_DENSE_ATTR)

    def ignore_time_dense_attr_hex(self) -> None:
        """Time lexing a 1024x1024xi8 dense attribute given as a hex string."""
        Component.lex_file(Component.WORKLOAD_LARGE_DENSE_ATTR_HEX)


class ParsePhase(Component):
    """Benchmark the xDSL parser on MLIR files."""

    def time_constant_100(self) -> None:
        """Time parsing constant folding for 100 items."""
        Component.parse_operation(Component.WORKLOAD_CONSTANT_100)

    def time_constant_1000(self) -> None:
        """Time parsing constant folding for 100 items."""
        Component.parse_operation(Component.WORKLOAD_CONSTANT_1000)

    def ignore_time_dense_attr(self) -> None:
        """Time parsing a 1024x1024xi8 dense attribute."""
        Component.parse_operation(Component.WORKLOAD_LARGE_DENSE_ATTR)

    def time_dense_attr_hex(self) -> None:
        """Time parsing a 1024x1024xi8 dense attribute given as a hex string."""
        Component.parse_operation(Component.WORKLOAD_LARGE_DENSE_ATTR_HEX)


class PatternRewritePhase(Component):
    """Benchmark rewriting in xDSL."""

    PARSED_CONSTANT_100 = Component.parse_module(Component.WORKLOAD_CONSTANT_100)
    PARSED_CONSTANT_1000 = Component.parse_module(Component.WORKLOAD_CONSTANT_1000)
    PARSED_LARGE_DENSE_ATTR_HEX = Component.parse_module(
        Component.WORKLOAD_LARGE_DENSE_ATTR_HEX
    )

    def time_constant_100(self) -> None:
        """Time pattern rewriting 100 items with the constant folding pass."""
        Component.constant_fold_module(PatternRewritePhase.PARSED_CONSTANT_100)

    def time_constant_1000(self) -> None:
        """Time pattern rewriting 1000 items with the constant folding pass."""
        Component.constant_fold_module(PatternRewritePhase.PARSED_CONSTANT_1000)

    def time_canonicalize_100(self) -> None:
        """Time canonicalising constant folding for 100 items."""
        Component.canonicalize_module(PatternRewritePhase.PARSED_CONSTANT_100)

    def time_canonicalize_1000(self) -> None:
        """Time canonicalising constant folding for 1000 items."""
        Component.canonicalize_module(PatternRewritePhase.PARSED_CONSTANT_1000)

    def time_dense_attr_hex(self) -> None:
        """Time canonicalising a 1024x1024xi8 dense attribute given as a hex string."""
        Component.canonicalize_module(PatternRewritePhase.PARSED_LARGE_DENSE_ATTR_HEX)

    def time_lower_scf_to_cf(self) -> None:
        """Time lowering a module from the `scf` to the `cf` dialect."""
        raise NotImplementedError()


class VerifyPhase:
    """Benchmark verifying in xDSL."""

    PARSED_CONSTANT_100 = Component.parse_module(Component.WORKLOAD_CONSTANT_100)
    PARSED_CONSTANT_1000 = Component.parse_module(Component.WORKLOAD_CONSTANT_1000)
    PARSED_LARGE_DENSE_ATTR_HEX = Component.parse_module(
        Component.WORKLOAD_LARGE_DENSE_ATTR_HEX
    )

    def time_constant_100(self) -> None:
        """Time verifying constant folding for 100 items."""
        Component.verify_module(VerifyPhase.PARSED_CONSTANT_100)

    def time_constant_1000(self) -> None:
        """Time verifying constant folding for 1000 items."""
        Component.verify_module(VerifyPhase.PARSED_CONSTANT_1000)

    def time_dense_attr_hex(self) -> None:
        """Time verifying a 1024x1024xi8 dense attribute given as a hex string."""
        Component.verify_module(VerifyPhase.PARSED_LARGE_DENSE_ATTR_HEX)


class PrintPhase:
    """Benchmark printing in xDSL."""

    PARSED_CONSTANT_100 = Component.parse_module(Component.WORKLOAD_CONSTANT_100)
    PARSED_CONSTANT_1000 = Component.parse_module(Component.WORKLOAD_CONSTANT_1000)
    PARSED_LARGE_DENSE_ATTR_HEX = Component.parse_module(
        Component.WORKLOAD_LARGE_DENSE_ATTR_HEX
    )

    def time_constant_100(self) -> None:
        """Time printing constant folding for 100 items."""
        Component.print_module(PrintPhase.PARSED_CONSTANT_100)

    def time_constant_1000(self) -> None:
        """Time printing constant folding for 1000 items."""
        Component.print_module(PrintPhase.PARSED_CONSTANT_1000)

    def time_dense_attr_hex(self) -> None:
        """Time printing a 1024x1024xi8 dense attribute given as a hex string."""
        Component.print_module(PrintPhase.PARSED_LARGE_DENSE_ATTR_HEX)


if __name__ == "__main__":
    from collections.abc import Callable

    from bench_utils import profile

    LEXER = LexPhase()
    PARSER = ParsePhase()
    PATTERN_REWRITER = PatternRewritePhase()
    VERIFIER = VerifyPhase()
    PRINTER = PrintPhase()

    BENCHMARKS: dict[str, Callable[[], None]] = {
        "Lexer.empty_program": LEXER.time_empty_program,
        "Lexer.constant_100": LEXER.time_constant_100,
        "Lexer.constant_1000": LEXER.time_constant_1000,
        # "Lexer.dense_attr": LEXER.ignore_time_dense_attr,
        "Lexer.dense_attr_hex": LEXER.ignore_time_dense_attr_hex,
        "Parser.constant_100": PARSER.time_constant_100,
        "Parser.constant_1000": PARSER.time_constant_1000,
        # "Parser.dense_attr": PARSER.ignore_time_dense_attr,
        "Parser.dense_attr_hex": PARSER.time_dense_attr_hex,
        "PatternRewriter.constant_100": PATTERN_REWRITER.time_constant_100,
        "PatternRewriter.canonicalize_100": PATTERN_REWRITER.time_canonicalize_100,
        "PatternRewriter.constant_1000": PATTERN_REWRITER.time_constant_1000,
        "PatternRewriter.canonicalize_1000": PATTERN_REWRITER.time_canonicalize_1000,
        "PatternRewriter.dense_attr_hex": PATTERN_REWRITER.time_dense_attr_hex,
        "Verifier.constant_100": VERIFIER.time_constant_100,
        "Verifier.constant_1000": VERIFIER.time_constant_1000,
        "Verifier.dense_attr_hex": VERIFIER.time_dense_attr_hex,
        "Printer.constant_100": PRINTER.time_constant_100,
        "Printer.constant_1000": PRINTER.time_constant_1000,
        "Printer.dense_attr_hex": PRINTER.time_dense_attr_hex,
    }
    profile(BENCHMARKS)
