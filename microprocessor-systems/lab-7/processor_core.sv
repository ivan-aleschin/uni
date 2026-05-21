module processor_core (
  input  logic        clk_i,
  input  logic        rst_i,

  input  logic        stall_i,
  input  logic [31:0] instr_i,
  input  logic [31:0] mem_rd_i,
  input  logic        irq_req_i,

  output logic [31:0] instr_addr_o,
  output logic [31:0] mem_addr_o,
  output logic [ 2:0] mem_size_o,
  output logic        mem_req_o,
  output logic        mem_we_o,
  output logic [31:0] mem_wd_o,
  output logic        irq_ret_o
);

  import decoder_pkg::*;

  logic        trap;
  logic [31:0] actual_mcause;
  logic        illegal_instr;
  logic        irq_signal;
  logic [31:0] irq_cause;

  assign trap = irq_signal | illegal_instr;
  assign actual_mcause = illegal_instr ? 32'h0000_0002 : irq_cause;

  logic [31:0] pc_reg, next_pc;

  always_ff @(posedge clk_i) begin
    if (rst_i)
      pc_reg <= 32'd0;
    else if (!stall_i || trap)
      pc_reg <= next_pc;
  end

  assign instr_addr_o = pc_reg;

  logic [31:0] imm_I, imm_S, imm_B, imm_U, imm_J, imm_Z;
  assign imm_I = {{20{instr_i[31]}}, instr_i[31:20]};
  assign imm_S = {{20{instr_i[31]}}, instr_i[31:25], instr_i[11:7]};
  assign imm_B = {{20{instr_i[31]}}, instr_i[7], instr_i[30:25], instr_i[11:8], 1'b0};
  assign imm_U = {instr_i[31:12], 12'b0};
  assign imm_J = {{12{instr_i[31]}}, instr_i[19:12], instr_i[20], instr_i[30:21], 1'b0};
  assign imm_Z = {27'b0, instr_i[19:15]};

  logic [1:0] a_sel;
  logic [2:0] b_sel;
  logic [4:0] alu_op;
  logic [2:0] csr_op;
  logic       csr_we, gpr_we, branch, jal, jalr, mret;
  logic [1:0] wb_sel;

  logic       mem_req_core;
  logic       mem_we_core;

  decoder main_decoder (
    .fetched_instr_i (instr_i),
    .a_sel_o         (a_sel),
    .b_sel_o         (b_sel),
    .alu_op_o        (alu_op),
    .csr_op_o        (csr_op),
    .csr_we_o        (csr_we),
    .mem_req_o       (mem_req_core),
    .mem_we_o        (mem_we_core),
    .mem_size_o      (mem_size_o),
    .gpr_we_o        (gpr_we),
    .wb_sel_o        (wb_sel),
    .illegal_instr_o (illegal_instr),
    .branch_o        (branch),
    .jal_o           (jal),
    .jalr_o          (jalr),
    .mret_o          (mret)
  );

  logic [31:0] rd1, rd2, write_data;

  register_file gpr (
    .clk_i          (clk_i),
    .write_enable_i (gpr_we & ~(stall_i | trap)),
    .write_addr_i   (instr_i[11:7]),
    .read_addr1_i   (instr_i[19:15]),
    .read_addr2_i   (instr_i[24:20]),
    .write_data_i   (write_data),
    .read_data1_o   (rd1),
    .read_data2_o   (rd2)
  );

  assign mem_wd_o = rd2;

  logic [31:0] alu_a, alu_b, alu_result;
  logic        alu_flag;

  always_comb begin
    case (a_sel)
      OP_A_RS1     : alu_a = rd1;
      OP_A_CURR_PC : alu_a = pc_reg;
      OP_A_ZERO    : alu_a = 32'd0;
      default      : alu_a = rd1;
    endcase
  end

  always_comb begin
    case (b_sel)
      OP_B_RS2   : alu_b = rd2;
      OP_B_IMM_I : alu_b = imm_I;
      OP_B_IMM_U : alu_b = imm_U;
      OP_B_IMM_S : alu_b = imm_S;
      OP_B_INCR  : alu_b = 32'd4;
      default    : alu_b = rd2;
    endcase
  end

  alu main_alu (
    .a_i      (alu_a),
    .b_i      (alu_b),
    .alu_op_i (alu_op),
    .flag_o   (alu_flag),
    .result_o (alu_result)
  );

  assign mem_addr_o = alu_result;

  logic [31:0] csr_rd, mie_data, mepc_data, mtvec_data;

  csr_controller csr_unit (
    .clk_i          (clk_i),
    .rst_i          (rst_i),
    .trap_i         (trap),
    .opcode_i       (csr_op),
    .addr_i         (instr_i[31:20]),
    .pc_i           (pc_reg),
    .mcause_i       (actual_mcause),
    .rs1_data_i     (rd1),
    .imm_data_i     (imm_Z),
    .write_enable_i (csr_we),
    .read_data_o    (csr_rd),
    .mie_o          (mie_data),
    .mepc_o         (mepc_data),
    .mtvec_o        (mtvec_data)
  );

  interrupt_controller int_ctrl (
    .clk_i       (clk_i),
    .rst_i       (rst_i),
    .exception_i (illegal_instr),
    .irq_req_i   (irq_req_i),
    .mie_i       (mie_data[0]),
    .mret_i      (mret),
    .irq_ret_o   (irq_ret_o),
    .irq_cause_o (irq_cause),
    .irq_o       (irq_signal)
  );

  always_comb begin
    case (wb_sel)
      WB_EX_RESULT : write_data = alu_result;
      WB_LSU_DATA  : write_data = mem_rd_i;
      WB_CSR_DATA  : write_data = csr_rd;
      default      : write_data = alu_result;
    endcase
  end

  always_comb begin
    if (mret)
      next_pc = mepc_data;
    else if (trap)
      next_pc = mtvec_data;
    else if (jalr)
      next_pc = (rd1 + imm_I) & ~32'd1;
    else if (branch && alu_flag)
      next_pc = pc_reg + imm_B;
    else if (jal)
      next_pc = pc_reg + imm_J;
    else
      next_pc = pc_reg + 32'd4;
  end

  assign mem_req_o = mem_req_core & !trap;
  assign mem_we_o  = mem_we_core  & !trap;

endmodule