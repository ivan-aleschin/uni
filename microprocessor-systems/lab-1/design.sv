// ============================================================
// 1-битный полный сумматор
// ============================================================
module fulladder(
  input  logic a_i,
  input  logic b_i,
  input  logic carry_i,
  output logic sum_o,
  output logic carry_o
);
  assign sum_o   = a_i ^ b_i ^ carry_i;
  assign carry_o = (a_i & b_i) | (a_i & carry_i) | (b_i & carry_i);
endmodule

// ============================================================
// 4-битный сумматор — цепочка из четырёх 1-битных
// ============================================================
module fulladder4(
  input  logic [3:0] a_i,
  input  logic [3:0] b_i,
  input  logic       carry_i,
  output logic [3:0] sum_o,
  output logic       carry_o
);
  logic [3:1] carry_mid; // промежуточные переносы между разрядами

  fulladder fa0 (.a_i(a_i[0]), .b_i(b_i[0]), .carry_i(carry_i),      .sum_o(sum_o[0]), .carry_o(carry_mid[1]));
  fulladder fa1 (.a_i(a_i[1]), .b_i(b_i[1]), .carry_i(carry_mid[1]), .sum_o(sum_o[1]), .carry_o(carry_mid[2]));
  fulladder fa2 (.a_i(a_i[2]), .b_i(b_i[2]), .carry_i(carry_mid[2]), .sum_o(sum_o[2]), .carry_o(carry_mid[3]));
  fulladder fa3 (.a_i(a_i[3]), .b_i(b_i[3]), .carry_i(carry_mid[3]), .sum_o(sum_o[3]), .carry_o(carry_o));
endmodule

// ============================================================
// 32-битный сумматор — цепочка из восьми 4-битных
// ============================================================
module fulladder32(
  input  logic [31:0] a_i,
  input  logic [31:0] b_i,
  input  logic        carry_i,
  output logic [31:0] sum_o,
  output logic        carry_o
);
  logic [7:1] carry_mid; // промежуточные переносы между 4-битными блоками

  fulladder4 fa4_0 (.a_i(a_i[ 3: 0]), .b_i(b_i[ 3: 0]), .carry_i(carry_i),      .sum_o(sum_o[ 3: 0]), .carry_o(carry_mid[1]));
  fulladder4 fa4_1 (.a_i(a_i[ 7: 4]), .b_i(b_i[ 7: 4]), .carry_i(carry_mid[1]), .sum_o(sum_o[ 7: 4]), .carry_o(carry_mid[2]));
  fulladder4 fa4_2 (.a_i(a_i[11: 8]), .b_i(b_i[11: 8]), .carry_i(carry_mid[2]), .sum_o(sum_o[11: 8]), .carry_o(carry_mid[3]));
  fulladder4 fa4_3 (.a_i(a_i[15:12]), .b_i(b_i[15:12]), .carry_i(carry_mid[3]), .sum_o(sum_o[15:12]), .carry_o(carry_mid[4]));
  fulladder4 fa4_4 (.a_i(a_i[19:16]), .b_i(b_i[19:16]), .carry_i(carry_mid[4]), .sum_o(sum_o[19:16]), .carry_o(carry_mid[5]));
  fulladder4 fa4_5 (.a_i(a_i[23:20]), .b_i(b_i[23:20]), .carry_i(carry_mid[5]), .sum_o(sum_o[23:20]), .carry_o(carry_mid[6]));
  fulladder4 fa4_6 (.a_i(a_i[27:24]), .b_i(b_i[27:24]), .carry_i(carry_mid[6]), .sum_o(sum_o[27:24]), .carry_o(carry_mid[7]));
  fulladder4 fa4_7 (.a_i(a_i[31:28]), .b_i(b_i[31:28]), .carry_i(carry_mid[7]), .sum_o(sum_o[31:28]), .carry_o(carry_o));
endmodule
