module processor_system (
  input  logic        clk_i,
  input  logic        resetn_i,

  // Peripheral pins. Only PS/2 and HEX are used in this variant.
  input  logic [15:0] sw_i,
  output logic [15:0] led_o,

  input  logic        kclk_i,
  input  logic        kdata_i,
  output logic [ 6:0] hex_led_o,
  output logic [ 7:0] hex_sel_o,

  input  logic        rx_i,
  output logic        tx_o,

  output logic [ 3:0] vga_r_o,
  output logic [ 3:0] vga_g_o,
  output logic [ 3:0] vga_b_o,
  output logic        vga_hs_o,
  output logic        vga_vs_o
);

  localparam logic [7:0] DEV_DMEM = 8'h00;
  localparam logic [7:0] DEV_PS2  = 8'h03;
  localparam logic [7:0] DEV_HEX  = 8'h04;

  logic sysclk;
  logic rst;

  sys_clk_rst_gen divider (
    .ex_clk_i       (clk_i),
    .ex_areset_n_i  (resetn_i),
    .div_i          (4'd5),
    .sys_clk_o      (sysclk),
    .sys_reset_o    (rst)
  );

  logic [31:0] instr_addr;
  logic [31:0] instr_data;

  logic [31:0] core_addr;
  logic        core_req;
  logic        core_we;
  logic [ 2:0] core_size;
  logic [31:0] core_wd;
  logic [31:0] core_rd;
  logic        stall_sig;

  logic [31:0] mem_addr;
  logic        mem_req;
  logic        mem_we;
  logic [ 3:0] mem_be;
  logic [31:0] mem_wd;
  logic [31:0] mem_rd;

  logic [31:0] dmem_rd;
  logic [31:0] ps2_rd;
  logic [31:0] hex_rd;

  logic        dmem_req;
  logic        ps2_req;
  logic        hex_req;
  logic [31:0] periph_addr;

  logic        ps2_irq_req;
  logic        irq_req;
  logic        irq_ret;

  assign periph_addr = {8'h00, mem_addr[23:0]};

  assign dmem_req = mem_req && (mem_addr[31:24] == DEV_DMEM);
  assign ps2_req  = mem_req && (mem_addr[31:24] == DEV_PS2);
  assign hex_req  = mem_req && (mem_addr[31:24] == DEV_HEX);

  assign irq_req = ps2_irq_req;

  // Unused peripheral pins in this variant.
  assign led_o   = 16'h0000;
  assign tx_o    = 1'b1;
  assign vga_r_o = 4'h0;
  assign vga_g_o = 4'h0;
  assign vga_b_o = 4'h0;
  assign vga_hs_o = 1'b0;
  assign vga_vs_o = 1'b0;

  processor_core core (
    .clk_i        (sysclk),
    .rst_i        (rst),
    .stall_i      (stall_sig),
    .instr_i      (instr_data),
    .mem_rd_i     (core_rd),
    .irq_req_i    (irq_req),
    .instr_addr_o (instr_addr),
    .mem_addr_o   (core_addr),
    .mem_size_o   (core_size),
    .mem_req_o    (core_req),
    .mem_we_o     (core_we),
    .mem_wd_o     (core_wd),
    .irq_ret_o    (irq_ret)
  );

  lsu lsu_unit (
    .clk_i        (sysclk),
    .rst_i        (rst),
    .core_req_i   (core_req),
    .core_we_i    (core_we),
    .core_size_i  (core_size),
    .core_addr_i  (core_addr),
    .core_wd_i    (core_wd),
    .mem_rd_i     (mem_rd),
    .core_rd_o    (core_rd),
    .core_stall_o (stall_sig),
    .mem_req_o    (mem_req),
    .mem_we_o     (mem_we),
    .mem_be_o     (mem_be),
    .mem_addr_o   (mem_addr),
    .mem_wd_o     (mem_wd),
    .mem_ready_i  (1'b1)
  );

  instr_mem imem (
    .read_addr_i (instr_addr),
    .read_data_o (instr_data)
  );

  data_mem dmem (
    .clk_i          (sysclk),
    .mem_req_i      (dmem_req),
    .write_enable_i (mem_we),
    .byte_enable_i  (mem_be),
    .addr_i         (mem_addr),
    .write_data_i   (mem_wd),
    .read_data_o    (dmem_rd)
  );

  ps2_sb_ctrl ps2_ctrl (
    .clk_i               (sysclk),
    .rst_i               (rst),
    .addr_i              (periph_addr),
    .req_i               (ps2_req),
    .write_data_i        (mem_wd),
    .write_enable_i      (mem_we),
    .read_data_o         (ps2_rd),
    .interrupt_request_o (ps2_irq_req),
    .interrupt_return_i  (irq_ret),
    .kclk_i              (kclk_i),
    .kdata_i             (kdata_i)
  );

  hex_sb_ctrl hex_ctrl (
    .clk_i          (sysclk),
    .rst_i          (rst),
    .addr_i         (periph_addr),
    .req_i          (hex_req),
    .write_data_i   (mem_wd),
    .write_enable_i (mem_we),
    .read_data_o    (hex_rd),
    .hex_led        (hex_led_o),
    .hex_sel        (hex_sel_o)
  );

  always_comb begin
    unique case (mem_addr[31:24])
      DEV_DMEM: mem_rd = dmem_rd;
      DEV_PS2 : mem_rd = ps2_rd;
      DEV_HEX : mem_rd = hex_rd;
      default : mem_rd = 32'h0000_0000;
    endcase
  end

endmodule
