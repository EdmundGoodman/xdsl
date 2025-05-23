#!/usr/bin/env python3
"""Microbenchmark properties of the xDSL implementation."""

import importlib

import xdsl.dialects.arith
import xdsl.dialects.builtin


class LoadDialects:
    """Benchmark loading dialects in xDSL."""

    def time_arith_load(self) -> None:
        """Time loading the `arith` dialect.

        Note that this must be done with `importlib.reload` rather than just
        directly importing with `from xdsl.dialects.arith import Arith` to avoid
        tests interacting with each other.
        """
        importlib.reload(xdsl.dialects.arith)

    def time_builtin_load(self) -> None:
        """Time loading the `builtin` dialect."""
        importlib.reload(xdsl.dialects.builtin)


if __name__ == "__main__":
    from bench_utils import Benchmark, profile

    LOAD_DIALECTS = LoadDialects()

    profile(
        {
            "LoadDialects.arith_load": Benchmark(LOAD_DIALECTS.time_arith_load),
            "LoadDialects.builtin_load": Benchmark(LOAD_DIALECTS.time_builtin_load),
        }
    )
