"builtin.module"() ({
  %0:2 = "test.op"() : () -> (tensor<2x4x3xf32>, tensor<4x2xf32>)
  %1 = "onnx.MatMul"(%0#0, %0#1) {onnx_node_name = "/MatMul"} : (tensor<2x4x3xf32>, tensor<4x2xf32>) -> tensor<2x2xf32>
}) : () -> ()
