#!/usr/bin/env python3
"""Microbenchmark properties of the xDSL implementation."""

from __future__ import annotations

import importlib

import xdsl.dialects.arith
import xdsl.dialects.builtin
from xdsl.dialects.builtin import LocationAttr
from xdsl.dialects.gpu import TerminatorOp
from xdsl.dialects.test import TestOp
from xdsl.ir import Block
from xdsl.irdl import (
    IRDLOperation,
    irdl_op_definition,
    opt_successor_def,
    traits_def,
)
from xdsl.traits import IsTerminator, NoTerminator


@irdl_op_definition
class IsTerminatorOp(IRDLOperation):
    """An operation that provides the IsTerminator trait."""

    name = "test.is_terminator"
    successor = opt_successor_def()
    traits = traits_def(IsTerminator())


@irdl_op_definition
class EmptyOp(IRDLOperation):
    """An empty operation."""

    name = "empty"

    def __init__(self):
        super().__init__(attributes={"testbench.empty": LocationAttr})


class IRTraversal:
    """Benchmark the time to traverse xDSL IR."""

    EXAMPLE_BLOCK_NUM_OPS = 1_000
    EXAMPLE_OPS = (TestOp() for _ in range(EXAMPLE_BLOCK_NUM_OPS))
    EXAMPLE_BLOCK = Block(ops=EXAMPLE_OPS)

    def time_iterate_ops(self) -> None:
        """Time directly iterating over a python list of operations.

        Comparison with `for (Operation *op : /*std::vector*/ops) {` at
        0.35ns/op.
        """
        for op in IRTraversal.EXAMPLE_OPS:
            assert op

    def time_iterate_block_ops(self) -> None:
        """Time directly iterating over the linked list of a block's operations.

        Comparison with `for (Operation &op : *block) {` at 2.15ns/op.
        """
        for op in IRTraversal.EXAMPLE_BLOCK.ops:
            assert op

    def time_walk_block_ops(self) -> None:
        """Time walking a block's operations.

        Comparison with `block->walk([](Operation *op) {});` with no region in
        the IR at 6.11ns/op.
        """
        for op in IRTraversal.EXAMPLE_BLOCK.walk():
            assert op


class Extensibility:
    """Benchmark the time to check interface and trait properties."""

    from xdsl.dialects.builtin import (
        UnregisteredOp,  # noqa: F401 # pyright: ignore[reportUnusedImport]
    )

    IS_TERMINATOR_OP = TerminatorOp()

    def time_interface_check(self) -> None:
        """Time checking the class hierarchy of an operation.

        Indirect comparison with `assert( dyn_cast<InterfaceT>(op) )` at
        9.68ns/op.

        This is not a direct comparison as xDSL does not use the
        class hierarchy to express interface functionality, but is interesting
        to compare `isinstance` with `dyn_cast` in context.
        """
        assert isinstance(Extensibility.IS_TERMINATOR_OP, TerminatorOp)

    def time_trait_check(self) -> None:
        """Time checking the trait of an operation.

        Comparison with `assert( op->hasTrait<TraitT>(op) )` at 18.1ns/op.

        Note that the class instantiation includes
        `from xdsl.dialects.builtin import UnregisteredOp` to avoid measuring
        the cost of import machinery in the `has_trait` method.
        """
        assert Extensibility.IS_TERMINATOR_OP.has_trait(IsTerminator)

    def time_trait_check_neg(self) -> None:
        """Time checking the trait of an operation.

        Comparison with `assert( ! op->hasTrait<TraitT>(op) )` at 13.4ns/op.

        Note that the class instantiation includes
        `from xdsl.dialects.builtin import UnregisteredOp` to avoid measuring
        the cost of import machinery in the `has_trait` method.
        """
        assert not Extensibility.IS_TERMINATOR_OP.has_trait(NoTerminator)


class OpCreation:
    """Benchmark creating an operation in xDSL."""

    CONSTANT_OPERATION_X_SIZE = 6
    CONSTANT_OPERATION_Y_SIZE = 6
    CONSTANT_OPERATION = EmptyOp()

    def time_operation_create(self) -> None:
        """Time creating an empty operation.

        Comparison with `OperationState opState(unknownLoc, "testbench.empty");
        Operation::create(opState)` at 118ns/op.
        """
        EmptyOp()

    def time_operation_clone(self) -> None:
        """Time cloning an empty operation.

        Comparison with `OwningOpRef<ModuleOp> moduleClone = moduleOp->clone();`
        at 631ns/op.
        """
        OpCreation.CONSTANT_OPERATION.clone()


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


class ImportClasses:
    """Benchmark the time to import xDSL classes."""

    def ignore_time_import_xdsl_opt(self) -> None:
        """Import benchmark using the default asv mechanism."""
        from xdsl.xdsl_opt_main import (
            xDSLOptMain,  # noqa: F401 # pyright: ignore[reportUnusedImport]
        )

    def timeraw_import_xdsl_opt(self) -> str:
        """Import benchmark using the `raw` asv mechanism."""
        return """
        from xdsl.xdsl_opt_main import xDSLOptMain
        """


if __name__ == "__main__":
    from collections.abc import Callable

    from bench_utils import profile

    EXTENSIBILITY = Extensibility()
    IMPORT_CLASSES = ImportClasses()
    IR_TRAVERSAL = IRTraversal()
    LOAD_DIALECTS = LoadDialects()
    OP_CREATION = OpCreation()

    BENCHMARKS: dict[str, Callable[[], None]] = {
        "IRTraversal.iterate_ops": IR_TRAVERSAL.time_iterate_ops,
        "IRTraversal.iterate_block_ops": IR_TRAVERSAL.time_iterate_block_ops,
        "IRTraversal.walk_block_ops": IR_TRAVERSAL.time_walk_block_ops,
        "Extensibility.interface_check": EXTENSIBILITY.time_interface_check,
        "Extensibility.trait_check": EXTENSIBILITY.time_trait_check,
        "Extensibility.trait_check_neg": EXTENSIBILITY.time_trait_check_neg,
        "OpCreation.operation_create": OP_CREATION.time_operation_create,
        "OpCreation.operation_clone": OP_CREATION.time_operation_clone,
        "LoadDialects.arith_load": LOAD_DIALECTS.time_arith_load,
        "LoadDialects.builtin_load": LOAD_DIALECTS.time_builtin_load,
        "ImportClasses.import_xdsl_opt": IMPORT_CLASSES.ignore_time_import_xdsl_opt,
    }
    profile(BENCHMARKS)
