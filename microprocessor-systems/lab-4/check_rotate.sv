// Самопроверяющий тестбенч для индивидуального задания (вариант 1: rotate right)
// Прогоняет несколько значений sw_i и сравнивает out_o с эталонным rotate

`timescale 1ns/1ps

module check_rotate();
  logic        clk;
  logic        rst;
  logic [15:0] sw_i;
  logic [31:0] out_o;

  CYBERcobra DUT (
    .clk_i(clk),
    .rst_i(rst),
    .sw_i (sw_i),
    .out_o(out_o)
  );

  initial clk = 0;
  always #5 clk = ~clk;

  // Эталон: rotate right на k бит для 32-битного значения
  function automatic logic [31:0] ror32(input logic [31:0] a, input logic [4:0] k);
    ror32 = (a >> k) | (a << ((32 - k) & 5'h1F));
  endfunction

  integer err = 0;
  logic [31:0] expected;
  // a в программе захардкожена константой 11
  localparam logic [31:0] A_CONST = 32'd11;

  task automatic check_case(input logic [4:0] k);
    sw_i = {11'd0, k};
    rst  = 1'b1;
    @(posedge clk); @(posedge clk);
    rst  = 1'b0;
    // Программа выполняет 10 инструкций, последняя — бесконечный цикл out=r9.
    // Ждём достаточно тактов чтобы PC дошёл до loop.
    repeat (30) @(posedge clk);
    expected = ror32(A_CONST, k);
    if (out_o !== expected) begin
      $display("FAIL k=%0d  expected=%h  got=%h", k, expected, out_o);
      err = err + 1;
    end else begin
      $display("OK   k=%0d  out=%h", k, out_o);
    end
  endtask

  initial begin
    $dumpfile("wave_check.vcd");
    $dumpvars(0, check_rotate);
    sw_i = '0; rst = 1'b1;
    @(posedge clk); @(posedge clk);

    check_case(5'd0);
    check_case(5'd1);
    check_case(5'd2);
    check_case(5'd4);
    check_case(5'd8);
    check_case(5'd16);
    check_case(5'd31);

    if (err == 0) $display("\n[PASS] rotate-right test (variant 1): all cases OK\n");
    else          $display("\n[FAIL] rotate-right test: %0d errors\n", err);
    $finish;
  end
endmodule
