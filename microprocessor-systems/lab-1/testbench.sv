`timescale 1ns/1ps

module testbench();

  logic a, b, cin, sum, cout;

  fulladder DUT_fa(
    .a_i(a), .b_i(b), .carry_i(cin),
    .sum_o(sum), .carry_o(cout)
  );

  logic [31:0] a32, b32, sum32;
  logic        cin32, cout32;

  fulladder32 DUT_fa32(
    .a_i(a32), .b_i(b32), .carry_i(cin32),
    .sum_o(sum32), .carry_o(cout32)
  );

  task check32(input [31:0] va, vb, input vc, input [31:0] expected_sum, input expected_carry);
    a32 = va; b32 = vb; cin32 = vc;
    #10ns;
    if (sum32 !== expected_sum || cout32 !== expected_carry)
      $display("FAIL: %0d + %0d + %0d = %0d (carry=%0b), ожидалось %0d (carry=%0b)",
               va, vb, vc, sum32, cout32, expected_sum, expected_carry);
    else
      $display("OK:   %0d + %0d + %0d = %0d", va, vb, vc, sum32);
  endtask

  initial begin
    // --- Запись временной диаграммы ---
    $dumpfile("wave.vcd");
    $dumpvars(0, testbench);

    // --- 1-битный сумматор: все 8 комбинаций ---
    $display("=== fulladder (1 бит) ===");
    {a, b, cin} = 3'b000; #10ns;
    {a, b, cin} = 3'b001; #10ns;
    {a, b, cin} = 3'b010; #10ns;
    {a, b, cin} = 3'b011; #10ns;
    {a, b, cin} = 3'b100; #10ns;
    {a, b, cin} = 3'b101; #10ns;
    {a, b, cin} = 3'b110; #10ns;
    {a, b, cin} = 3'b111; #10ns;

    // --- 32-битный сумматор ---
    $display("=== fulladder32 (32 бита) ===");
    check32(0,           0,           0, 0,           0);
    check32(1,           1,           0, 2,           0);
    check32(42,          79,          0, 121,         0);
    check32(32'hFFFFFFFF, 1,          0, 0,           1);
    check32(32'hFFFFFFFF, 32'hFFFFFFFF, 0, 32'hFFFFFFFE, 1);
    check32(100,         200,         1, 301,         0);

    $display("=== Готово ===");
    $finish;
  end

endmodule
