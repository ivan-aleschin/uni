`timescale 1ns/1ps

module testbench();

  // ----------------------------------------------------------------
  // Сигналы
  // ----------------------------------------------------------------
  logic        clk;
  logic        we;
  logic [ 4:0] wa, ra1, ra2;
  logic [31:0] wd, rd1, rd2;

  // ----------------------------------------------------------------
  // DUT
  // ----------------------------------------------------------------
  register_file DUT (
    .clk_i         (clk),
    .write_enable_i(we ),
    .write_addr_i  (wa ),
    .read_addr1_i  (ra1),
    .read_addr2_i  (ra2),
    .write_data_i  (wd ),
    .read_data1_o  (rd1),
    .read_data2_o  (rd2)
  );

  // ----------------------------------------------------------------
  // Тактовый сигнал: период 10 ns
  // ----------------------------------------------------------------
  initial clk = 0;
  always #5ns clk = ~clk;

  int err_cnt = 0;

  // Запись значения и проверка через один такт
  task write_and_check(
    input [ 4:0] addr,
    input [31:0] data,
    input [31:0] expected1,  // ожидаемое на rd1
    input [31:0] expected2,  // ожидаемое на rd2
    input [63:0] test_num
  );
    @(posedge clk); #1ns;
    wa = addr; wd = data; we = 1'b1;
    ra1 = addr; ra2 = addr;
    @(posedge clk); #1ns;
    we = 1'b0;
    if (rd1 !== expected1) begin
      err_cnt++;
      $display("FAIL #%0d write addr=%0d data=0x%08h | rd1=0x%08h expected=0x%08h",
               test_num, addr, data, rd1, expected1);
    end
    if (rd2 !== expected2) begin
      err_cnt++;
      $display("FAIL #%0d write addr=%0d data=0x%08h | rd2=0x%08h expected=0x%08h",
               test_num, addr, data, rd2, expected2);
    end
  endtask

  initial begin
    $dumpfile("wave.vcd");
    $dumpvars(0, testbench);

    we = 0; wa = 0; ra1 = 0; ra2 = 0; wd = 0;

    $display("=== Тест регистрового файла — начало ===\n");

    // ----------------------------------------------------------------
    // Регистр 0 всегда равен 0
    // ----------------------------------------------------------------
    ra1 = 5'd0; ra2 = 5'd0;
    @(posedge clk); #1ns;
    if (rd1 !== 32'd0) begin
      err_cnt++;
      $display("FAIL #1: reg[0] читается как 0x%08h, ожидалось 0x00000000", rd1);
    end

    // Попытка записи в регистр 0 — должно игнорироваться
    @(posedge clk); #1ns;
    wa = 5'd0; wd = 32'hDEADBEEF; we = 1'b1;
    @(posedge clk); #1ns;
    we = 1'b0;
    ra1 = 5'd0;
    @(posedge clk); #1ns;
    if (rd1 !== 32'd0) begin
      err_cnt++;
      $display("FAIL #2: запись в reg[0] не должна работать, rd1=0x%08h", rd1);
    end else
      $display("OK #2: запись в reg[0] корректно игнорируется");

    // ----------------------------------------------------------------
    // Запись и чтение через регистры 1–31
    // ----------------------------------------------------------------
    write_and_check(5'd1,  32'h00000001, 32'h00000001, 32'h00000001, 3);
    write_and_check(5'd2,  32'h00000002, 32'h00000002, 32'h00000002, 4);
    write_and_check(5'd15, 32'hABCDEF01, 32'hABCDEF01, 32'hABCDEF01, 5);
    write_and_check(5'd31, 32'hFFFFFFFF, 32'hFFFFFFFF, 32'hFFFFFFFF, 6);

    // ----------------------------------------------------------------
    // write_enable = 0: значение не должно меняться
    // ----------------------------------------------------------------
    @(posedge clk); #1ns;
    wa = 5'd1; wd = 32'hCAFEBABE; we = 1'b0; // WE выключен
    @(posedge clk); #1ns;
    ra1 = 5'd1;
    @(posedge clk); #1ns;
    if (rd1 !== 32'h00000001) begin
      err_cnt++;
      $display("FAIL #7: запись при WE=0 не должна работать, rd1=0x%08h", rd1);
    end else
      $display("OK #7: WE=0 корректно блокирует запись");

    // ----------------------------------------------------------------
    // Два независимых порта чтения
    // ----------------------------------------------------------------
    @(posedge clk); #1ns;
    ra1 = 5'd1; ra2 = 5'd2;
    @(posedge clk); #1ns;
    if (rd1 !== 32'h00000001 || rd2 !== 32'h00000002) begin
      err_cnt++;
      $display("FAIL #8: порты чтения: rd1=0x%08h (exp 0x00000001), rd2=0x%08h (exp 0x00000002)",
               rd1, rd2);
    end else
      $display("OK #8: два порта чтения работают независимо");

    // ----------------------------------------------------------------
    // Асинхронное чтение: данные доступны сразу после смены адреса
    // ----------------------------------------------------------------
    ra1 = 5'd15;
    #1ns; // без ожидания фронта
    if (rd1 !== 32'hABCDEF01) begin
      err_cnt++;
      $display("FAIL #9: асинхронное чтение: rd1=0x%08h (exp 0xABCDEF01)", rd1);
    end else
      $display("OK #9: чтение асинхронное");

    // ----------------------------------------------------------------
    // Итог
    // ----------------------------------------------------------------
    $display("\n=== Тест завершён. Ошибок: %0d ===\n", err_cnt);
    $finish;
  end

endmodule
