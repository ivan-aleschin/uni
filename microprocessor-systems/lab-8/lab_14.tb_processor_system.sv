/* -----------------------------------------------------------------------------
* Project Name   : Architectures of Processor Systems (APS) lab work
* Organization   : National Research University of Electronic Technology (MIET)
* Department     : Institute of Microdevices and Control Systems
* Author(s)      : Andrei Solodovnikov
* Email(s)       : hepoh@org.miet.ru
* ------------------------------------------------------------------------------
*/

/* ЛР14 (вариант ps2_hex): тестбенч.
   Алгоритм теста:
     1. Выставить ps2_i = scan_code
     2. Подать однотактный импульс irq_req (иначе irq_pending не даст выйти из обработчика)
     3. Дождаться irq_ret (mret в _int_handler)
     4. Проверить hex0_o == (scan_code & 0xF) и hex1_o == (scan_code >> 4)
*/
module lab_14_tb_processor_system ();

  // -------------------------------------------------------------------------
  // Сигналы
  // -------------------------------------------------------------------------
  reg         clk;
  reg         rst;
  reg         irq_req;
  wire        irq_ret;
  reg  [31:0] ps2_val;
  wire [31:0] hex0_val;
  wire [31:0] hex1_val;

  // -------------------------------------------------------------------------
  // DUT
  // -------------------------------------------------------------------------
  processor_system DUT (
    .clk_i    (clk),
    .rst_i    (rst),
    .irq_req_i(irq_req),
    .irq_ret_o(irq_ret),
    .ps2_i    (ps2_val),
    .hex0_o   (hex0_val),
    .hex1_o   (hex1_val)
  );

  // -------------------------------------------------------------------------
  // Тактовый генератор
  // -------------------------------------------------------------------------
  initial clk = 0;
  always  #10 clk = ~clk;

  // -------------------------------------------------------------------------
  // Watchdog
  // -------------------------------------------------------------------------
  initial begin
    repeat (20000) @(posedge clk);
    $display("[WATCHDOG] Тест прерван по таймауту");
    $finish;
  end

  // -------------------------------------------------------------------------
  // VCD
  // -------------------------------------------------------------------------
  initial begin
    $dumpfile("wave.vcd");
    $dumpvars(0, lab_14_tb_processor_system);
  end

  // -------------------------------------------------------------------------
  // Монитор: каждый такт печатаем PC и hex-выходы
  // -------------------------------------------------------------------------
  always @(posedge clk) begin
    if (!rst)
      $display("Time=%0t PC=%h Instr=%h HEX0=%h HEX1=%h IRQ_RET=%b",
               $time, DUT.core.instr_addr_o, DUT.core.instr_i,
               hex0_val, hex1_val, irq_ret);
  end

  // -------------------------------------------------------------------------
  // Тестовая последовательность: три PS/2 scan-кода
  // -------------------------------------------------------------------------
  integer pass_cnt;
  integer fail_cnt;

  task run_test;
    input [7:0] code;
    reg [31:0] exp_hex0;
    reg [31:0] exp_hex1;
    begin
      exp_hex0 = {28'b0, code[3:0]};
      exp_hex1 = {28'b0, code[7:4]};

      ps2_val = {24'b0, code};
      irq_req = 0;

      // Дать startup'у время отработать (BSS + CSR init + вход в main)
      repeat (400) @(posedge clk);

      $display("\n[TEST] IRQ: ps2=0x%02h  ожидаем hex0=0x%h hex1=0x%h",
               code, exp_hex0, exp_hex1);

      // Импульс ровно 1 такт: без этого interrupt_controller бесконечно
      // переповторяет trap (mie_reg остаётся ненулевым после сброса mstatus.MIE).
      @(posedge clk); irq_req = 1;
      @(posedge clk); irq_req = 0;

      // Ожидаем irq_ret (mret в _int_handler) до 3000 тактов
      fork
        begin : wait_ret
          while (irq_ret !== 1'b1) @(posedge clk);
        end
        begin : timeout
          repeat (3000) @(posedge clk);
        end
      join_any
      disable wait_ret;
      disable timeout;

      repeat (20) @(posedge clk);

      if (hex0_val === exp_hex0 && hex1_val === exp_hex1) begin
        $display("[PASS] ps2=0x%02h → hex0=0x%h hex1=0x%h", code, hex0_val, hex1_val);
        pass_cnt = pass_cnt + 1;
      end else begin
        $display("[FAIL] ps2=0x%02h → hex0=0x%h (ожидалось 0x%h), hex1=0x%h (ожидалось 0x%h)",
                 code, hex0_val, exp_hex0, hex1_val, exp_hex1);
        fail_cnt = fail_cnt + 1;
      end
    end
  endtask

  initial begin
    pass_cnt = 0;
    fail_cnt = 0;

    irq_req  = 0;
    ps2_val  = 0;
    rst      = 1;
    #40;
    rst = 0;

    run_test(8'h1C);   // scan 0x1C: hex0=0xC, hex1=0x1
    run_test(8'h32);   // scan 0x32: hex0=0x2, hex1=0x3
    run_test(8'hAB);   // scan 0xAB: hex0=0xB, hex1=0xA

    $display("\n=== Итог: %0d/3 тестов прошло ===", pass_cnt);
    $finish;
  end

endmodule
