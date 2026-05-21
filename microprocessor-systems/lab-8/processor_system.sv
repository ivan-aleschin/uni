/* -----------------------------------------------------------------------------
* Project Name   : Architectures of Processor Systems (APS) lab work
* Organization   : National Research University of Electronic Technology (MIET)
* Department     : Institute of Microdevices and Control Systems
* Author(s)      : Andrei Solodovnikov
* Email(s)       : hepoh@org.miet.ru
* ------------------------------------------------------------------------------
*/

/* ЛР14 (вариант ps2_hex): расширение processor_system декодером периферийной шины.
   Карта адресов (верхний байт):
     0x00 → data_mem (RAM 2 КБ)
     0x03 → PS/2 клавиатура (scan_code = ps2_i, только чтение в симуляции)
     0x04 → Семисегментные дисплеи (hex0 @ offset 0, hex1 @ offset 4)
*/
module processor_system (
  input  logic        clk_i,
  input  logic        rst_i,
  input  logic        irq_req_i,
  output logic        irq_ret_o,

  // PS/2 scan code (управляется тестбенчем)
  input  logic [31:0] ps2_i,

  // Выходы семисегментных дисплеев (проверяются тестбенчем)
  output logic [31:0] hex0_o,
  output logic [31:0] hex1_o
);

  // ---------------------------------------------------------------------------
  // Сигналы
  // ---------------------------------------------------------------------------
  logic [31:0] instr_addr;
  logic [31:0] instr;

  logic [31:0] core_mem_addr;
  logic [ 2:0] core_mem_size;
  logic        core_mem_req;
  logic        core_mem_we;
  logic [31:0] core_mem_wd;
  logic [31:0] core_mem_rd;
  logic        core_stall;

  logic [31:0] ext_mem_addr;
  logic [31:0] ext_mem_wd;
  logic        ext_mem_we;
  logic [ 3:0] ext_mem_be;
  logic        ext_mem_req;
  logic [31:0] ext_mem_rd;

  // ---------------------------------------------------------------------------
  // Декодер адресного пространства (верхний байт адреса)
  // ---------------------------------------------------------------------------
  logic is_data_mem;
  logic is_ps2;
  logic is_hex;

  assign is_data_mem = (ext_mem_addr[31:24] == 8'h00);
  assign is_ps2      = (ext_mem_addr[31:24] == 8'h03);
  assign is_hex      = (ext_mem_addr[31:24] == 8'h04);

  // ---------------------------------------------------------------------------
  // Регистры семисегментных дисплеев (hex0 = offset 0, hex1 = offset 4)
  // ---------------------------------------------------------------------------
  always_ff @(posedge clk_i) begin
    if (rst_i) begin
      hex0_o <= 32'h0;
      hex1_o <= 32'h0;
    end else if (ext_mem_we && is_hex) begin
      case (ext_mem_addr[4:2])
        3'd0: hex0_o <= ext_mem_wd;
        3'd1: hex1_o <= ext_mem_wd;
      endcase
    end
  end

  // ---------------------------------------------------------------------------
  // Мультиплексор чтения: PS/2 возвращает scan_code; иначе data_mem
  // ---------------------------------------------------------------------------
  logic [31:0] dmem_rd;
  assign ext_mem_rd = is_ps2 ? ps2_i : dmem_rd;

  // ---------------------------------------------------------------------------
  // Ядро процессора
  // ---------------------------------------------------------------------------
  processor_core core (
    .clk_i        (clk_i),
    .rst_i        (rst_i),
    .stall_i      (core_stall),
    .instr_i      (instr),
    .mem_rd_i     (core_mem_rd),
    .irq_req_i    (irq_req_i),

    .instr_addr_o (instr_addr),
    .mem_addr_o   (core_mem_addr),
    .mem_size_o   (core_mem_size),
    .mem_req_o    (core_mem_req),
    .mem_we_o     (core_mem_we),
    .mem_wd_o     (core_mem_wd),
    .irq_ret_o    (irq_ret_o)
  );

  // ---------------------------------------------------------------------------
  // LSU
  // ---------------------------------------------------------------------------
  lsu lsu_unit (
    .clk_i      (clk_i),
    .rst_i      (rst_i),

    .addr_i     (core_mem_addr),
    .wd_i       (core_mem_wd),
    .size_i     (core_mem_size),
    .req_i      (core_mem_req),
    .we_i       (core_mem_we),
    .rd_o       (core_mem_rd),
    .stall_o    (core_stall),

    .mem_addr_o (ext_mem_addr),
    .mem_wd_o   (ext_mem_wd),
    .mem_we_o   (ext_mem_we),
    .mem_be_o   (ext_mem_be),
    .mem_req_o  (ext_mem_req),
    .mem_rd_i   (ext_mem_rd)
  );

  // ---------------------------------------------------------------------------
  // Памяти
  // ---------------------------------------------------------------------------
  instr_mem imem (
    .addr_i      (instr_addr),
    .read_data_o (instr)
  );

  data_mem dmem (
    .clk_i (clk_i),
    .addr_i (ext_mem_addr),
    .we_i   (ext_mem_we && is_data_mem),
    .be_i   (ext_mem_be),
    .wd_i   (ext_mem_wd),
    .rd_o   (dmem_rd)
  );

endmodule
