/* -----------------------------------------------------------------------------
* Project Name   : Architectures of Processor Systems (APS) lab work
* Organization   : National Research University of Electronic Technology (MIET)
* Department     : Institute of Microdevices and Control Systems
* Author(s)      : Andrei Solodovnikov
* Email(s)       : hepoh@org.miet.ru
* ------------------------------------------------------------------------------
*/
module processor_system (
  input  logic clk_i,
  input  logic rst_i,
  input  logic irq_req_i,
  output logic irq_ret_o
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
  // LSU (Load-Store Unit) - Интеграция из ЛР9
  // ---------------------------------------------------------------------------
  lsu lsu_unit (
    .clk_i        (clk_i),
    .rst_i        (rst_i),

    .addr_i       (core_mem_addr),
    .wd_i         (core_mem_wd),
    .size_i       (core_mem_size),
    .req_i        (core_mem_req),
    .we_i         (core_mem_we),
    .rd_o         (core_mem_rd),
    .stall_o      (core_stall),

    .mem_addr_o   (ext_mem_addr),
    .mem_wd_o     (ext_mem_wd),
    .mem_we_o     (ext_mem_we),
    .mem_be_o     (ext_mem_be),
    .mem_req_o    (ext_mem_req),
    .mem_rd_i     (ext_mem_rd)
  );

  // ---------------------------------------------------------------------------
  // Память
  // ---------------------------------------------------------------------------
  instr_mem imem (
    .addr_i       (instr_addr),
    .read_data_o  (instr)
  );

  data_mem dmem (
    .clk_i        (clk_i),
    .addr_i       (ext_mem_addr),
    .we_i         (ext_mem_we),
    .be_i         (ext_mem_be),
    .wd_i         (ext_mem_wd),
    .rd_o         (ext_mem_rd)
  );

endmodule
