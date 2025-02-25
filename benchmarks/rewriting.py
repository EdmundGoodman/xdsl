#!/usr/bin/env python3
"""Benchmarks for the pattern rewriter of the xDSL implementation."""

from benchmarks.workloads import WorkloadBuilder
from xdsl.context import Context
from xdsl.dialects.arith import Arith
from xdsl.dialects.builtin import Builtin, ModuleOp
from xdsl.parser import Parser as XdslParser
from xdsl.printer import Printer
from xdsl.transforms.canonicalize import CanonicalizePass

CTX = Context(allow_unregistered=True)
CTX.load_dialect(Arith)
CTX.load_dialect(Builtin)

MODULE_PRINTER = Printer()


def parse_module(contents: str) -> ModuleOp:
    """Parse a MLIR file as a module."""
    parser = XdslParser(CTX, contents)
    return parser.parse_module()


EMPTY_WORKLOAD = parse_module(WorkloadBuilder.empty())
CONSTANT_WORKLOAD = parse_module(WorkloadBuilder.constant_folding(2000))
FMADD_WORKLOAD = parse_module(WorkloadBuilder.fmadd(100))


class PatternRewritePhase:
    """Benchmark rewriting in xDSL."""

    def time_constant_folding(self) -> None:
        """Time canonicalizing constant folding."""
        CanonicalizePass().apply(CTX, CONSTANT_WORKLOAD)

    def time_fmadd(self) -> None:
        """Time canonicalizing fused multiply-adds."""
        CanonicalizePass().apply(CTX, FMADD_WORKLOAD)


if __name__ == "__main__":
    from collections.abc import Callable

    from bench_utils import profile

    PATTERN_REWRITER = PatternRewritePhase()
    BENCHMARKS: dict[str, Callable[[], None]] = {
        "PatternRewriter.constant_folding": PATTERN_REWRITER.time_constant_folding,
        "PatternRewriter.fmadd": PATTERN_REWRITER.time_fmadd,
    }
    profile(BENCHMARKS)

    # MODULE_PRINTER.print_op(FMADD_WORKLOAD)
