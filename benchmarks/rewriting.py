#!/usr/bin/env python3
"""Benchmarks for the pattern rewriter of the xDSL implementation."""

from benchmarks.helpers import get_context, parse_module
from benchmarks.workloads import WorkloadBuilder
from xdsl.dialects.arith import Arith
from xdsl.dialects.builtin import Builtin
from xdsl.transforms.canonicalize import CanonicalizePass

CTX = get_context()
CTX.load_dialect(Arith)
CTX.load_dialect(Builtin)


class PatternRewrite:
    """Benchmark rewriting in xDSL."""

    # WORKLOAD_CONSTANT_20 = parse_module(CTX, WorkloadBuilder.constant_folding(20))
    WORKLOAD_CONSTANT_100 = parse_module(CTX, WorkloadBuilder.constant_folding(100))
    # WORKLOAD_CONSTANT_500 = parse_module(CTX, WorkloadBuilder.constant_folding(500))
    WORKLOAD_CONSTANT_1000 = parse_module(CTX, WorkloadBuilder.constant_folding(1000))
    # WORKLOAD_CONSTANT_2000 = parse_module(CTX, WorkloadBuilder.constant_folding(2000))
    # WORKLOAD_CONSTANT_10000 = parse_module(CTX, WorkloadBuilder.constant_folding(10000))
    # WORKLOAD_CONSTANT_100000 = parse_module(CTX, WorkloadBuilder.constant_folding(100000))

    # TODO: Does this cost dominate?
    # CANONICALIZE_PASS = CanonicalizePass()

    # def time_constant_folding_20(self) -> None:
    #     """Time canonicalizing constant folding."""
    #     CanonicalizePass().apply(CTX, PatternRewrite.WORKLOAD_CONSTANT_20)

    def time_constant_folding_100(self) -> None:
        """Time canonicalizing constant folding."""
        CanonicalizePass().apply(CTX, PatternRewrite.WORKLOAD_CONSTANT_100)

    # def time_constant_folding_500(self) -> None:
    #     """Time canonicalizing constant folding."""
    #     CanonicalizePass().apply(CTX, PatternRewrite.WORKLOAD_CONSTANT_500)

    def time_constant_folding_1000(self) -> None:
        """Time canonicalizing constant folding."""
        CanonicalizePass().apply(CTX, PatternRewrite.WORKLOAD_CONSTANT_1000)

    # def time_constant_folding_2000(self) -> None:
    #     """Time canonicalizing constant folding."""
    #     CanonicalizePass().apply(CTX, PatternRewrite.WORKLOAD_CONSTANT_2000)

    # def time_constant_folding_10000(self) -> None:
    #     """Time canonicalizing constant folding."""
    #     CanonicalizePass().apply(CTX, PatternRewrite.WORKLOAD_CONSTANT_10000)

    # def time_constant_folding_100000(self) -> None:
    #     """Time canonicalizing constant folding."""
    #     CanonicalizePass().apply(CTX, PatternRewrite.WORKLOAD_CONSTANT_100000)


if __name__ == "__main__":
    from collections.abc import Callable

    from bench_utils import profile

    PATTERN_REWRITER = PatternRewrite()
    BENCHMARKS: dict[str, Callable[[], None]] = {
        # "PatternRewriter.constant_folding_20": PATTERN_REWRITER.time_constant_folding_20,
        "PatternRewriter.constant_folding_100": PATTERN_REWRITER.time_constant_folding_100,
        # "PatternRewriter.constant_folding_500": PATTERN_REWRITER.time_constant_folding_500,
        "PatternRewriter.constant_folding_1000": PATTERN_REWRITER.time_constant_folding_1000,
        # "PatternRewriter.constant_folding_2000": PATTERN_REWRITER.time_constant_folding_2000,
        # "PatternRewriter.constant_folding_10000": PATTERN_REWRITER.time_constant_folding_10000,
        # "PatternRewriter.constant_folding_100000": PATTERN_REWRITER.time_constant_folding_100000,
    }
    profile(BENCHMARKS)
