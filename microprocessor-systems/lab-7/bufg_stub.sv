// Заглушка примитива BUFG (clock buffer) от Xilinx для локальной симуляции.
// В Vivado/xsim BUFG автоматически разрешается из библиотеки unisim — этот файл
// в проект Vivado добавлять НЕ нужно. Здесь он только чтобы Verilator/iverilog
// могли скомпилировать sys_clk_rst_gen.sv.

`ifndef SYNTHESIS
module BUFG (
  output logic O,
  input  logic I
);
  assign O = I;
endmodule
`endif
