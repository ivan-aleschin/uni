// Модули сумматора из Лабораторной работы №1
// Подключается отдельным файлом при компиляции — не через import

module fulladder (
  input  logic a_i,
  input  logic b_i,
  input  logic carry_i,
  output logic sum_o,
  output logic carry_o
);
  assign sum_o   = a_i ^ b_i ^ carry_i;
  assign carry_o = (a_i & b_i) | (a_i & carry_i) | (b_i & carry_i);
endmodule

module fulladder4 (
  input  logic [3:0] a_i,
  input  logic [3:0] b_i,
  input  logic       carry_i,
  output logic [3:0] sum_o,
  output logic       carry_o
);
  logic [3:1] c;

  fulladder fa0 (.a_i(a_i[0]), .b_i(b_i[0]), .carry_i(carry_i), .sum_o(sum_o[0]), .carry_o(c[1]));
  fulladder fa1 (.a_i(a_i[1]), .b_i(b_i[1]), .carry_i(c[1]),    .sum_o(sum_o[1]), .carry_o(c[2]));
  fulladder fa2 (.a_i(a_i[2]), .b_i(b_i[2]), .carry_i(c[2]),    .sum_o(sum_o[2]), .carry_o(c[3]));
  fulladder fa3 (.a_i(a_i[3]), .b_i(b_i[3]), .carry_i(c[3]),    .sum_o(sum_o[3]), .carry_o(carry_o));
endmodule

module fulladder32 (
  input  logic [31:0] a_i,
  input  logic [31:0] b_i,
  input  logic        carry_i,
  output logic [31:0] sum_o,
  output logic        carry_o
);
  logic [7:1] c;

  fulladder4 fa0 (.a_i(a_i[ 3: 0]), .b_i(b_i[ 3: 0]), .carry_i(carry_i), .sum_o(sum_o[ 3: 0]), .carry_o(c[1]));
  fulladder4 fa1 (.a_i(a_i[ 7: 4]), .b_i(b_i[ 7: 4]), .carry_i(c[1]),    .sum_o(sum_o[ 7: 4]), .carry_o(c[2]));
  fulladder4 fa2 (.a_i(a_i[11: 8]), .b_i(b_i[11: 8]), .carry_i(c[2]),    .sum_o(sum_o[11: 8]), .carry_o(c[3]));
  fulladder4 fa3 (.a_i(a_i[15:12]), .b_i(b_i[15:12]), .carry_i(c[3]),    .sum_o(sum_o[15:12]), .carry_o(c[4]));
  fulladder4 fa4 (.a_i(a_i[19:16]), .b_i(b_i[19:16]), .carry_i(c[4]),    .sum_o(sum_o[19:16]), .carry_o(c[5]));
  fulladder4 fa5 (.a_i(a_i[23:20]), .b_i(b_i[23:20]), .carry_i(c[5]),    .sum_o(sum_o[23:20]), .carry_o(c[6]));
  fulladder4 fa6 (.a_i(a_i[27:24]), .b_i(b_i[27:24]), .carry_i(c[6]),    .sum_o(sum_o[27:24]), .carry_o(c[7]));
  fulladder4 fa7 (.a_i(a_i[31:28]), .b_i(b_i[31:28]), .carry_i(c[7]),    .sum_o(sum_o[31:28]), .carry_o(carry_o));
endmodule
