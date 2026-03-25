`timescale 1ns/1ps

module testbench();
  import alu_opcodes_pkg::*;

  logic [ 4:0] op;
  logic [31:0] a, b;
  logic [31:0] result;
  logic        flag;

  alu DUT (
    .alu_op_i(op),
    .a_i     (a),
    .b_i     (b),
    .result_o(result),
    .flag_o  (flag)
  );

  int err_cnt = 0;

  // Задача проверки result_o
  task check_result(
    input [4:0]  t_op,
    input [31:0] t_a, t_b,
    input [31:0] expected,
    input [63:0] test_num
  );
    op = t_op; a = t_a; b = t_b;
    #5ns;
    if (result !== expected) begin
      err_cnt++;
      $display("FAIL #%0d op=%05b a=0x%08h b=0x%08h | result=0x%08h expected=0x%08h",
               test_num, t_op, t_a, t_b, result, expected);
    end
  endtask

  // Задача проверки flag_o
  task check_flag(
    input [4:0]  t_op,
    input [31:0] t_a, t_b,
    input        expected,
    input [63:0] test_num
  );
    op = t_op; a = t_a; b = t_b;
    #5ns;
    if (flag !== expected) begin
      err_cnt++;
      $display("FAIL #%0d op=%05b a=0x%08h b=0x%08h | flag=%b expected=%b",
               test_num, t_op, t_a, t_b, flag, expected);
    end
  endtask

  initial begin
    $dumpfile("wave.vcd");
    $dumpvars(0, testbench);

    $display("=== Тест АЛУ — начало ===\n");

    // ----------------------------------------------------------------
    // ADD — сложение через сумматор из ЛР1
    // ----------------------------------------------------------------
    check_result(ALU_ADD, 32'd0,          32'd0,          32'd0,          1);
    check_result(ALU_ADD, 32'd42,         32'd79,         32'd121,        2);
    check_result(ALU_ADD, 32'hFFFFFFFF,   32'd1,          32'd0,          3); // переполнение
    check_result(ALU_ADD, 32'h7FFFFFFF,   32'h00000001,   32'h80000000,   4);

    // ----------------------------------------------------------------
    // SUB — вычитание
    // ----------------------------------------------------------------
    check_result(ALU_SUB, 32'd10,         32'd3,          32'd7,          5);
    check_result(ALU_SUB, 32'd0,          32'd1,          32'hFFFFFFFF,   6); // underflow
    check_result(ALU_SUB, 32'd100,        32'd100,        32'd0,          7);

    // ----------------------------------------------------------------
    // AND, OR, XOR
    // ----------------------------------------------------------------
    check_result(ALU_AND, 32'hFF00FF00,   32'h0F0F0F0F,   32'h0F000F00,   8);
    check_result(ALU_OR,  32'hFF00FF00,   32'h0F0F0F0F,   32'hFF0FFF0F,   9);
    check_result(ALU_XOR, 32'hFF00FF00,   32'h0F0F0F0F,   32'hF00FF00F,   10);
    check_result(ALU_AND, 32'hAAAAAAAA,   32'h55555555,   32'h00000000,   11);
    check_result(ALU_OR,  32'hAAAAAAAA,   32'h55555555,   32'hFFFFFFFF,   12);

    // ----------------------------------------------------------------
    // SLL — логический сдвиг влево (только 5 младших бит b)
    // ----------------------------------------------------------------
    check_result(ALU_SLL, 32'h00000001,   32'd1,          32'h00000002,   13);
    check_result(ALU_SLL, 32'h00000001,   32'd31,         32'h80000000,   14);
    check_result(ALU_SLL, 32'hFFFFFFFF,   32'd1,          32'hFFFFFFFE,   15);
    check_result(ALU_SLL, 32'h00000001,   32'hFFFFFFE0,   32'h00000001,   16); // сдвиг на 0 (b[4:0]=0)

    // ----------------------------------------------------------------
    // SRL — логический сдвиг вправо
    // ----------------------------------------------------------------
    check_result(ALU_SRL, 32'h80000000,   32'd1,          32'h40000000,   17);
    check_result(ALU_SRL, 32'hFFFFFFFF,   32'd8,          32'h00FFFFFF,   18); // старшие биты = 0
    check_result(ALU_SRL, 32'h80000000,   32'd31,         32'h00000001,   19);

    // ----------------------------------------------------------------
    // SRA — арифметический сдвиг вправо (знак сохраняется)
    // ----------------------------------------------------------------
    check_result(ALU_SRA, 32'h80000000,   32'd1,          32'hC0000000,   20); // отрицательное → знак
    check_result(ALU_SRA, 32'hFFFFFFFF,   32'd8,          32'hFFFFFFFF,   21); // -1 >> 8 = -1
    check_result(ALU_SRA, 32'h7FFFFFFF,   32'd1,          32'h3FFFFFFF,   22); // положительное = логический

    // ----------------------------------------------------------------
    // SLTS — знаковое сравнение в result_o
    // ----------------------------------------------------------------
    check_result(ALU_SLTS, 32'hFFFFFFFF,  32'd1,          32'd1,          23); // -1 < 1
    check_result(ALU_SLTS, 32'd1,         32'hFFFFFFFF,   32'd0,          24); // 1 < -1 ? нет
    check_result(ALU_SLTS, 32'd5,         32'd5,          32'd0,          25); // равны

    // ----------------------------------------------------------------
    // SLTU — беззнаковое сравнение в result_o
    // ----------------------------------------------------------------
    check_result(ALU_SLTU, 32'hFFFFFFFF, 32'd1,           32'd0,          26); // 4294967295 < 1 ? нет
    check_result(ALU_SLTU, 32'd1,        32'hFFFFFFFF,    32'd1,          27); // 1 < 4294967295
    check_result(ALU_SLTU, 32'd0,        32'd0,           32'd0,          28); // равны

    // ----------------------------------------------------------------
    // Проверка default: неизвестный опкод → result=0, flag=0
    // ----------------------------------------------------------------
    check_result(5'b11110, 32'hDEADBEEF, 32'hDEADBEEF,   32'd0,          29);
    check_flag  (5'b11110, 32'hDEADBEEF, 32'hDEADBEEF,   1'b0,           30);

    // ----------------------------------------------------------------
    // EQ — равенство
    // ----------------------------------------------------------------
    check_flag(ALU_EQ, 32'd42,         32'd42,         1'b1,             31);
    check_flag(ALU_EQ, 32'd42,         32'd43,         1'b0,             32);
    check_flag(ALU_EQ, 32'hFFFFFFFF,   32'hFFFFFFFF,   1'b1,             33);

    // ----------------------------------------------------------------
    // NE — неравенство
    // ----------------------------------------------------------------
    check_flag(ALU_NE, 32'd42,         32'd42,         1'b0,             34);
    check_flag(ALU_NE, 32'd42,         32'd43,         1'b1,             35);

    // ----------------------------------------------------------------
    // LTS — знаковое <
    // ----------------------------------------------------------------
    check_flag(ALU_LTS, 32'hFFFFFFFF,  32'd1,          1'b1,             36); // -1 < 1
    check_flag(ALU_LTS, 32'd1,         32'hFFFFFFFF,   1'b0,             37); // 1 < -1 ? нет
    check_flag(ALU_LTS, 32'd5,         32'd5,          1'b0,             38); // равны

    // ----------------------------------------------------------------
    // GES — знаковое >=
    // ----------------------------------------------------------------
    check_flag(ALU_GES, 32'd5,         32'd5,          1'b1,             39); // равны
    check_flag(ALU_GES, 32'd6,         32'd5,          1'b1,             40); // больше
    check_flag(ALU_GES, 32'hFFFFFFFF,  32'd1,          1'b0,             41); // -1 >= 1 ? нет

    // ----------------------------------------------------------------
    // LTU — беззнаковое <
    // ----------------------------------------------------------------
    check_flag(ALU_LTU, 32'd1,         32'hFFFFFFFF,   1'b1,             42); // 1 < 4294967295
    check_flag(ALU_LTU, 32'hFFFFFFFF,  32'd1,          1'b0,             43);
    check_flag(ALU_LTU, 32'd0,         32'd0,          1'b0,             44);

    // ----------------------------------------------------------------
    // GEU — беззнаковое >=
    // ----------------------------------------------------------------
    check_flag(ALU_GEU, 32'hFFFFFFFF,  32'd1,          1'b1,             45);
    check_flag(ALU_GEU, 32'd1,         32'hFFFFFFFF,   1'b0,             46);
    check_flag(ALU_GEU, 32'd7,         32'd7,          1'b1,             47);

    // ----------------------------------------------------------------
    // Проверяем что flag=0 при вычислительных операциях
    // ----------------------------------------------------------------
    op = ALU_ADD; a = 32'd1; b = 32'd1; #5ns;
    if (flag !== 1'b0) begin
      err_cnt++;
      $display("FAIL #48: flag должен быть 0 для ALU_ADD, получено %b", flag);
    end
    op = ALU_AND; a = 32'hFF; b = 32'hFF; #5ns;
    if (flag !== 1'b0) begin
      err_cnt++;
      $display("FAIL #49: flag должен быть 0 для ALU_AND, получено %b", flag);
    end

    // ----------------------------------------------------------------
    // Проверяем что result=0 при операциях сравнения
    // ----------------------------------------------------------------
    op = ALU_EQ; a = 32'd5; b = 32'd5; #5ns;
    if (result !== 32'd0) begin
      err_cnt++;
      $display("FAIL #50: result должен быть 0 для ALU_EQ, получено 0x%08h", result);
    end

    $display("\n=== Тест завершён. Ошибок: %0d ===\n", err_cnt);
    $finish;
  end

endmodule
