// fulladder32 и его зависимости — в lab1_adders.sv
// Компиляция: iverilog -g2012 -o sim alu_opcodes_pkg.sv lab1_adders.sv design.sv testbench.sv

module alu (
  input  logic [ 4:0] alu_op_i,
  input  logic [31:0] a_i,
  input  logic [31:0] b_i,
  output logic [31:0] result_o,
  output logic        flag_o
);
  import alu_opcodes_pkg::*;

  // Подключение 32-битного сумматора из лабораторной №1
  logic [31:0] add_result;
  logic        add_carry;   // не используется в АЛУ, но порт должен быть подключён

  fulladder32 adder (
    .a_i    (a_i),
    .b_i    (b_i),
    .carry_i(1'b0),
    .sum_o  (add_result),
    .carry_o(add_carry)
  );

  // Мультиплексор вычислительных операций → result_o
  always_comb begin
    result_o = '0;
    case (alu_op_i)
      ALU_ADD:  result_o = add_result;
      ALU_SUB:  result_o = a_i - b_i;
      ALU_AND:  result_o = a_i & b_i;
      ALU_OR:   result_o = a_i | b_i;
      ALU_XOR:  result_o = a_i ^ b_i;
      ALU_SLL:  result_o = a_i << b_i[4:0];
      ALU_SRL:  result_o = a_i >> b_i[4:0];
      ALU_SRA:  result_o = $signed(a_i) >>> b_i[4:0];
      ALU_SLTS: result_o = ($signed(a_i) < $signed(b_i)) ? 32'd1 : 32'd0;
      ALU_SLTU: result_o = (a_i < b_i)                  ? 32'd1 : 32'd0;
      default:  result_o = '0;
    endcase
  end

  // Мультиплексор операций сравнения → flag_o
  always_comb begin
    flag_o = 1'b0;
    case (alu_op_i)
      ALU_EQ:  flag_o = (a_i == b_i);
      ALU_NE:  flag_o = (a_i != b_i);
      ALU_LTS: flag_o = ($signed(a_i) <  $signed(b_i));
      ALU_GES: flag_o = ($signed(a_i) >= $signed(b_i));
      ALU_LTU: flag_o = (a_i <  b_i);
      ALU_GEU: flag_o = (a_i >= b_i);
      default: flag_o = 1'b0;
    endcase
  end

endmodule
