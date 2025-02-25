#!/usr/bin/env python3
"""Workloads for benchmarking xDSL."""

import random


class WorkloadBuilder:
    """A helper class to programmatically build synthetic workloads."""

    @classmethod
    def wrap_module(cls, ops: list[str]) -> str:
        """Wrap a list of operations as a module."""
        workload = f'"builtin.module"() ({{\n  {"\n  ".join(ops)}\n}}) : () -> ()'
        return workload

    @classmethod
    def empty(cls) -> str:
        """Generate an empty module."""
        return WorkloadBuilder.wrap_module([])

    @classmethod
    def constant_folding(cls, size: int = 100) -> str:
        """Generate a constant folding workload of a given size."""
        assert size >= 0
        random.seed(0)
        ops: list[str] = []
        ops.append(
            '%0 = "arith.constant"() {"value" = '
            f"{random.randint(1, 1000)} : i32}} : () -> i32"
        )
        for i in range(1, size + 1):
            if i % 2 == 0:
                ops.append(
                    f'%{i} = "arith.addi"(%{i - 1}, %{i - 2}) : (i32, i32) -> i32'
                )
            else:
                ops.append(
                    f'%{i} = "arith.constant"() {{"value" = '
                    f"{random.randint(1, 1000)} : i32}} : () -> i32"
                )
        ops.append(f'"test.op"(%{size}) : (i32) -> ()')
        return WorkloadBuilder.wrap_module(ops)


class Workloads:
    """Static workload strings for benchmarking."""

    EMPTY = WorkloadBuilder.empty()
    WORKLOAD_4 = WorkloadBuilder.constant_folding(4)
    WORKLOAD_20 = WorkloadBuilder.constant_folding(20)
    WORKLOAD_100 = WorkloadBuilder.constant_folding(100)
    WORKLOAD_1000 = WorkloadBuilder.constant_folding(1000)
