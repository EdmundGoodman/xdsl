from typing import Any, cast, overload

import numpy as np
import numpy.typing as npt

from xdsl.dialects import onnx
from xdsl.dialects.builtin import (
    Float32Type,
    Float64Type,
    IntAttr,
    IntegerType,
    PackableType,
    TensorType,
)
from xdsl.interpreter import (
    Interpreter,
    InterpreterFunctions,
    ReturnedValues,
    impl,
    register_impls,
)
from xdsl.interpreters.builtin import xtype_for_el_type
from xdsl.interpreters.shaped_array import ShapedArray
from xdsl.interpreters.utils import ptr
from xdsl.utils.exceptions import InterpretationError


def to_dtype(
    xtype: PackableType[int] | PackableType[float],
) -> type[np.int32] | type[np.int64] | type[np.float32] | type[np.float64]:
    match xtype:
        case IntegerType(width=IntAttr(data=32)):
            return np.int32
        case IntegerType(width=IntAttr(data=64)):
            return np.int64
        case Float32Type():
            return np.float32
        case Float64Type():
            return np.float64
        case _:
            raise NotImplementedError()


def from_dtype(
    dtype: np.dtype[np.float32 | np.float64 | np.int32 | np.int64],
) -> PackableType[float] | PackableType[int]:
    if dtype == np.float32:
        return ptr.float32
    elif dtype == np.float64:
        return ptr.float64
    elif dtype == np.float32:
        return ptr.int32
    elif dtype == np.float64:
        return ptr.int64
    else:
        raise NotImplementedError()


@overload
def to_ndarray(
    shaped_array: ShapedArray[float],
) -> npt.NDArray[np.float32 | np.float64]: ...


@overload
def to_ndarray(
    shaped_array: ShapedArray[int],
) -> npt.NDArray[np.int32 | np.int64]: ...


def to_ndarray(
    shaped_array: ShapedArray[int] | ShapedArray[float],
) -> npt.NDArray[np.float32 | np.float64 | np.int32 | np.int64]:
    dtype = to_dtype(shaped_array.data_ptr.xtype)
    flat = np.frombuffer(shaped_array.data_ptr.raw.memory, dtype)
    shaped = flat.reshape(shaped_array.shape)
    return shaped


def from_ndarray(
    ndarray: npt.NDArray[np.float32 | np.float64 | np.int32 | np.int64],
) -> ShapedArray[float] | ShapedArray[int]:
    xtype = from_dtype(np.dtype(ndarray.dtype))
    # TypedPtr's generic parameter is invariant, so ambiguous here
    typed_ptr: ptr.TypedPtr[float] | ptr.TypedPtr[int] = ptr.TypedPtr(
        ptr.RawPtr(bytearray(ndarray.data)),
        xtype=xtype,  # pyright: ignore[reportArgumentType]
    )
    return ShapedArray(
        typed_ptr,
        list(ndarray.shape),
    )


@register_impls
class OnnxFunctions(InterpreterFunctions):
    @impl(onnx.AddOp)
    def run_add(
        self, interpreter: Interpreter, op: onnx.AddOp, args: tuple[Any, ...]
    ) -> tuple[Any, ...]:
        lhs, rhs = args[0], args[1]
        assert isinstance(lhs, ShapedArray)
        assert isinstance(rhs, ShapedArray)
        lhs = cast(ShapedArray[float], lhs)
        rhs = cast(ShapedArray[float], rhs)
        result = to_ndarray(lhs) + to_ndarray(rhs)
        return (from_ndarray(result),)

    @impl(onnx.SubOp)
    def run_sub(
        self, interpreter: Interpreter, op: onnx.SubOp, args: tuple[Any, ...]
    ) -> tuple[Any, ...]:
        lhs, rhs = args[0], args[1]
        assert isinstance(lhs, ShapedArray)
        assert isinstance(rhs, ShapedArray)
        lhs = cast(ShapedArray[float], lhs)
        rhs = cast(ShapedArray[float], rhs)
        result = to_ndarray(lhs) - to_ndarray(rhs)
        return (from_ndarray(result),)

    @impl(onnx.MulOp)
    def run_mul(
        self, interpreter: Interpreter, op: onnx.MulOp, args: tuple[Any, ...]
    ) -> tuple[Any, ...]:
        lhs, rhs = args[0], args[1]
        assert isinstance(lhs, ShapedArray)
        assert isinstance(rhs, ShapedArray)
        lhs = cast(ShapedArray[float], lhs)
        rhs = cast(ShapedArray[float], rhs)
        result = to_ndarray(lhs) * to_ndarray(rhs)
        return (from_ndarray(result),)

    @impl(onnx.DivOp)
    def run_div(
        self, interpreter: Interpreter, op: onnx.DivOp, args: tuple[Any, ...]
    ) -> tuple[Any, ...]:
        lhs, rhs = args[0], args[1]
        assert isinstance(lhs, ShapedArray)
        assert isinstance(rhs, ShapedArray)
        lhs = cast(ShapedArray[float], lhs)
        rhs = cast(ShapedArray[float], rhs)
        result = to_ndarray(lhs) / to_ndarray(rhs)
        return (from_ndarray(result),)

    @impl(onnx.ReluOp)
    def run_relu(
        self, interpreter: Interpreter, op: onnx.ReluOp, args: tuple[Any, ...]
    ) -> tuple[Any, ...]:
        operand = args[0]
        assert isinstance(operand, ShapedArray)
        operand = cast(ShapedArray[float], operand)
        operand_data = to_ndarray(operand)
        result = operand_data * (operand_data > 0)
        return (from_ndarray(result),)

    @impl(onnx.ConstantOp)
    def run_constant(
        self, interpreter: Interpreter, op: onnx.ConstantOp, args: tuple[Any, ...]
    ):
        if op.value is None:
            raise NotImplementedError("Only dense constant values implemented")
        shape = op.value.get_shape()
        data = op.value.get_values()
        data_ptr = ptr.TypedPtr[Any].new(
            data,
            xtype=xtype_for_el_type(
                op.value.get_element_type(), interpreter.index_bitwidth
            ),
        )
        return (ShapedArray(data_ptr, list(shape)),)

    @impl(onnx.ReshapeOp)
    def run_reshape(
        self, interpreter: Interpreter, op: onnx.ReshapeOp, args: tuple[Any, ...]
    ):
        if op.allow_zero is not None and op.allow_zero.value.data == 1:
            raise NotImplementedError(
                "allow_zero not yet supported in onnx.reshape interpreter"
            )
        input, new_shape = args
        assert isinstance(input, ShapedArray)
        assert isinstance(new_shape, ShapedArray)
        input = cast(ShapedArray[float], input)
        new_shape = cast(ShapedArray[int], new_shape)
        result_type = op.reshaped.type
        assert isinstance(result_type, TensorType)
        static_shape = list(result_type.get_shape())
        assert static_shape is not None
        if static_shape != new_shape.data:
            raise InterpretationError("Mismatch between static shape and new shape")
        return (input.with_shape(new_shape.data),)

    @impl(onnx.GemmOp)
    def run_gemm(
        self, interpreter: Interpreter, op: onnx.GemmOp, args: tuple[Any, ...]
    ):
        a, b, c = args[0], args[1], args[2]

        alpha = op.alpha.value.data if op.alpha is not None else 1.0
        beta = op.beta.value.data if op.beta is not None else 1.0

        assert isinstance(a, ShapedArray)
        assert isinstance(b, ShapedArray)
        assert isinstance(c, ShapedArray)

        a = cast(ShapedArray[float], a)
        b = cast(ShapedArray[float], b)
        c = cast(ShapedArray[float], c)

        nd_a = to_ndarray(a)
        nd_b = to_ndarray(b)
        nd_c = to_ndarray(c)

        if op.trans_a is not None and op.trans_a.value.data == 1:
            nd_a = np.transpose(nd_a)

        if op.trans_b is not None and op.trans_b.value.data == 1:
            nd_b = np.transpose(nd_b)

        result = alpha * nd_a @ nd_b + beta * nd_c

        return (from_ndarray(result),)

    @impl(onnx.ConvOp)
    def run_conv(
        self, interpreter: Interpreter, op: onnx.ConvOp, args: tuple[Any, ...]
    ):
        # initialise the attributes used
        auto_pad = op.auto_pad.data
        strides: list[int] = [value.value.data for value in op.strides]
        matrix, kernel, bias = args[0], args[1], args[2]
        pads: list[int] = [value.value.data for value in op.pads]

        matrix = cast(ShapedArray[float], matrix)
        kernel = cast(ShapedArray[float], kernel)
        bias = cast(ShapedArray[float], bias)

        matrix = to_ndarray(matrix)
        kernel = to_ndarray(kernel)

        if auto_pad != "NOTSET":
            if auto_pad == "SAME_UPPER" or auto_pad == "SAME_LOWER":
                out_height = int(np.ceil(matrix.shape[2] / strides[0]))
                out_width = int(np.ceil(matrix.shape[3] / strides[1]))

                pad_along_height = max(
                    (out_height - 1) * strides[0] + kernel.shape[2] - matrix.shape[2], 0
                )
                pad_along_width = max(
                    (out_width - 1) * strides[1] + kernel.shape[3] - matrix.shape[3], 0
                )

                if auto_pad == "SAME_UPPER":
                    pad_top = pad_along_height // 2
                    pad_bottom = pad_along_height - pad_top
                    pad_left = pad_along_width // 2
                    pad_right = pad_along_width - pad_left
                else:
                    pad_bottom = pad_along_height // 2
                    pad_top = pad_along_height - pad_bottom
                    pad_right = pad_along_width // 2
                    pad_left = pad_along_width - pad_right

                pads = [pad_top, pad_bottom, pad_left, pad_right]

            elif auto_pad == "VALID":
                pads = [0, 0, 0, 0]  # set padding to all zeros

        if pads:
            # case of asymmetric padding
            pad_values = [
                (pads[i], pads[i + len(pads) // 2]) for i in range(len(pads) // 2)
            ]

            # pad input matrix
            padded_matrix = np.pad(
                matrix,
                (
                    (0, 0),
                    (0, 0),
                    (pad_values[0][0], pad_values[0][1]),
                    (pad_values[1][0], pad_values[1][1]),
                ),
                mode="constant",
            )

            # padded shape case
            m_height, m_width = padded_matrix.shape[2:]

        else:
            m_height, m_width = matrix.shape[2:]

            padded_matrix = matrix

        # based on strides calculate the output shape
        out_height = int((m_height - kernel.shape[2]) // strides[0] + 1)
        out_width = int((m_width - kernel.shape[3]) // strides[1] + 1)

        output = np.zeros(
            (matrix.shape[0], matrix.shape[1], out_height, out_width),
            dtype=matrix.dtype,
        )

        # do convolution
        for k in range(matrix.shape[0]):
            for l in range(matrix.shape[1]):
                for i in range(0, m_height - kernel.shape[2] + 1, strides[0]):
                    for j in range(0, m_width - kernel.shape[3] + 1, strides[1]):
                        output[k, l, i // strides[0], j // strides[1]] = np.sum(
                            padded_matrix[
                                k, l, i : i + kernel.shape[2], j : j + kernel.shape[3]
                            ]
                            * kernel[k, l]
                        )

        output += to_ndarray(bias)

        # the number of channels is not always fixed to one
        result_type = op.res.type
        assert isinstance(result_type, TensorType)
        static_shape = list(result_type.get_shape())

        result = np.array(output)
        assert tuple(result.shape) == (
            1,
            static_shape[1],
            output.shape[2],
            output.shape[3],
        )
        return (from_ndarray(result),)

    @impl(onnx.MaxPoolSingleOutOp)
    def run_max_pool_single_out(
        self,
        interpreter: Interpreter,
        op: onnx.MaxPoolSingleOutOp,
        args: tuple[Any, ...],
    ):
        kernel_shape = tuple(value.value.data for value in op.kernel_shape)

        if len(kernel_shape) != 2:
            raise NotImplementedError("Only 2d max pooling supported")
        ky, kx = kernel_shape

        strides = tuple(value.value.data for value in op.strides)

        if len(strides) != 2:
            raise NotImplementedError("Only 2d max pooling supported")

        # initialise the attributes used
        auto_pad = op.auto_pad.data
        (matrix,) = args
        pads: list[int] = [value.value.data for value in op.pads]

        matrix = cast(ShapedArray[float], matrix)

        matrix = to_ndarray(matrix)

        if auto_pad != "NOTSET":
            if auto_pad == "SAME_UPPER" or auto_pad == "SAME_LOWER":
                out_height = int(np.ceil(matrix.shape[2] / strides[0]))
                out_width = int(np.ceil(matrix.shape[3] / strides[1]))

                pad_along_height = max(
                    (out_height - 1) * strides[0] + ky - matrix.shape[2], 0
                )
                pad_along_width = max(
                    (out_width - 1) * strides[1] + kx - matrix.shape[3], 0
                )

                if auto_pad == "SAME_UPPER":
                    pad_top = pad_along_height // 2
                    pad_bottom = pad_along_height - pad_top
                    pad_left = pad_along_width // 2
                    pad_right = pad_along_width - pad_left
                else:
                    pad_bottom = pad_along_height // 2
                    pad_top = pad_along_height - pad_bottom
                    pad_right = pad_along_width // 2
                    pad_left = pad_along_width - pad_right

                pads = [pad_top, pad_bottom, pad_left, pad_right]

            elif auto_pad == "VALID":
                pads = [0, 0, 0, 0]  # set padding to all zeros

        if pads:
            # case of asymmetric padding
            pad_values = [
                (pads[i], pads[i + len(pads) // 2]) for i in range(len(pads) // 2)
            ]

            # pad input matrix
            padded_matrix = np.pad(
                matrix,
                (
                    (0, 0),
                    (0, 0),
                    (pad_values[0][0], pad_values[0][1]),
                    (pad_values[1][0], pad_values[1][1]),
                ),
                mode="constant",
            )

            # padded shape case
            m_height, m_width = padded_matrix.shape[2:]

        else:
            m_height, m_width = matrix.shape[2:]

            padded_matrix = matrix

        # based on strides calculate the output shape
        out_height = int((m_height - ky) // strides[0] + 1)
        out_width = int((m_width - kx) // strides[1] + 1)

        result = np.zeros(
            (matrix.shape[0], matrix.shape[1], out_height, out_width),
            dtype=matrix.dtype,
        )

        # do maxpool computation
        for k in range(matrix.shape[0]):
            for l in range(matrix.shape[1]):
                for i in range(0, m_height - ky + 1, strides[0]):
                    for j in range(0, m_width - kx + 1, strides[1]):
                        result[k, l, i // strides[0], j // strides[1]] = np.nanmax(
                            padded_matrix[k, l, i : i + ky, j : j + kx]
                        )

        # Numpy has two types of ndarray: ndarray and NDArray, weirdly they don't seem
        # to be compatible, despite one being a typealias for the other...
        output: Any = result
        return (from_ndarray(output),)

    @impl(onnx.EntryPointOp)
    def run_entry_point(
        self, interpreter: Interpreter, op: onnx.EntryPointOp, args: tuple[Any, ...]
    ):
        return ReturnedValues(args), ()
