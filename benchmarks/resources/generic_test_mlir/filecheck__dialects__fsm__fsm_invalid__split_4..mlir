"builtin.module"() ({
  "fsm.machine"() ({
  ^bb0(%arg0: i1):
    %0 = "fsm.variable"() {initValue = 0 : i16, name = "cnt"} : () -> i16
    "fsm.state"() ({
      "fsm.output"() : () -> ()
    }, {
    }) {sym_name = "B"} : () -> ()
  }) {arg_names = ["argument"], function_type = () -> (), initialState = "B", sym_name = "foo"} : () -> ()
}) : () -> ()
