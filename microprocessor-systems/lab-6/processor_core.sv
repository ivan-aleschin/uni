/* -----------------------------------------------------------------------------
* Project Name   : Architectures of Processor Systems (APS) lab work
* Organization   : National Research University of Electronic Technology (MIET)
* Department     : Institute of Microdevices and Control Systems
* Author(s)      : Andrei Solodovnikov
* Email(s)       : hepoh@org.miet.ru
* ------------------------------------------------------------------------------
*/
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

  import alu_opcodes_pkg::*;
  import decoder_pkg::*;
  import csr_pkg::*;

  // ---------------------------------------------------------------------------
  // Декодер
  // ---------------------------------------------------------------------------
  logic [1:0] a_sel;
  logic [2:0] b_sel;
  logic [4:0] alu_op;
  logic [2:0] csr_op;
  logic       csr_we;
  logic       gpr_we;
  logic [1:0] wb_sel;
  logic       illegal_instr;
  logic       branch;
  logic       jal;
  logic       jalr;
  logic       mret;

  decoder dec (
    .fetched_instr_i (instr_i),
    .a_sel_o         (a_sel),
    .b_sel_o         (b_sel),
    .alu_op_o        (alu_op),
    .csr_op_o        (csr_op),
    .csr_we_o        (csr_we),
    .mem_req_o       (mem_req_o),
    .mem_we_o        (mem_we_o),
    .mem_size_o      (mem_size_o),
    .gpr_we_o        (gpr_we),
    .wb_sel_o        (wb_sel),
    .illegal_instr_o (illegal_instr),
    .branch_o        (branch),
    .jal_o           (jal),
    .jalr_o          (jalr),
    .mret_o          (mret)
  );

  // ---------------------------------------------------------------------------
  // Константы (Immediates)
  // ---------------------------------------------------------------------------
  logic [31:0] imm_I, imm_S, imm_B, imm_U, imm_J, imm_Z;
  assign imm_I = {{20{instr_i[31]}}, instr_i[31:20]};
  assign imm_S = {{20{instr_i[31]}}, instr_i[31:25], instr_i[11:7]};
  assign imm_B = {{19{instr_i[31]}}, instr_i[31], instr_i[7], instr_i[30:25], instr_i[11:8], 1'b0};
  assign imm_U = {instr_i[31:12], 12'b0};
  assign imm_J = {{11{instr_i[31]}}, instr_i[31], instr_i[19:12], instr_i[20], instr_i[30:21], 1'b0};
  assign imm_Z = {27'b0, instr_i[19:15]};

  // ---------------------------------------------------------------------------
  // Подсистема прерываний и CSR
  // ---------------------------------------------------------------------------
  logic trap;
  logic [31:0] trap_cause;
  logic [31:0] mtvec, mepc, csr_rd;
  logic mstatus_mie;
  logic [31:0] mie_reg;

  logic [31:0] csr_wd;
  assign csr_wd = csr_op[2] ? imm_Z : rd1;

  interrupt_controller int_ctrl (
    .clk_i         (clk_i),
    .rst_i         (rst_i),
    .irq_req_i     (irq_req_i),
    .mstatus_mie_i (mstatus_mie),
    .mie_reg_i     (mie_reg),
    .mret_i        (mret),
    .trap_o        (trap),
    .trap_cause_o  (trap_cause)
  );

  csr_controller csr_ctrl (
    .clk_i         (clk_i),
    .rst_i         (rst_i),
    .addr_i        (instr_i[31:20]),
    .wd_i          (csr_wd),
    .op_i          (csr_op),
    .we_i          (csr_we && !stall_i),
    .rd_o          (csr_rd),
    .trap_i        (trap && !stall_i),
    .trap_cause_i  (trap_cause),
    .trap_pc_i     (instr_addr_o),
    .mtvec_o       (mtvec),
    .mepc_o        (mepc),
    .mstatus_mie_o (mstatus_mie),
    .mie_reg_o     (mie_reg)
  );

  assign irq_ret_o = mret;

  // ---------------------------------------------------------------------------
  // Регистровый файл
  // ---------------------------------------------------------------------------
  logic [31:0] rd1, rd2, gpr_wd;
  register_file rf (
    .clk_i         (clk_i),
    .write_enable_i(gpr_we && !trap),
    .write_addr_i  (instr_i[11:7]),
    .read_addr1_i  (instr_i[19:15]),
    .read_addr2_i  (instr_i[24:20]),
    .write_data_i  (gpr_wd),
    .read_data1_o  (rd1),
    .read_data2_o  (rd2)
  );

  // ---------------------------------------------------------------------------
  // АЛУ
  // ---------------------------------------------------------------------------
  logic [31:0] operand_a, operand_b, alu_result;
  logic alu_flag;

  always_comb begin
    case (a_sel)
      OP_A_RS1:     operand_a = rd1;
      OP_A_CURR_PC: operand_a = instr_addr_o;
      OP_A_ZERO:    operand_a = 32'b0;
      default:      operand_a = 32'b0;
    endcase
  end

  always_comb begin
    case (b_sel)
      OP_B_RS2:   operand_b = rd2;
      OP_B_IMM_I: operand_b = imm_I;
      OP_B_IMM_U: operand_b = imm_U;
      OP_B_IMM_S: operand_b = imm_S;
      OP_B_INCR:  operand_b = 32'd4;
      default:    operand_b = 32'b0;
    endcase
  end

  alu alu_unit (.alu_op_i(alu_op), .a_i(operand_a), .b_i(operand_b), .result_o(alu_result), .flag_o(alu_flag));

  // ---------------------------------------------------------------------------
  // Writeback
  // ---------------------------------------------------------------------------
  always_comb begin
    case (wb_sel)
      WB_EX_RESULT: gpr_wd = alu_result;
      WB_LSU_DATA:  gpr_wd = mem_rd_i;
      WB_CSR_DATA:  gpr_wd = csr_rd;
      default:      gpr_wd = alu_result;
    endcase
  end

  assign mem_addr_o = alu_result;
  assign mem_wd_o   = rd2;

  // ---------------------------------------------------------------------------
  // PC Logic
  // ---------------------------------------------------------------------------
  logic [31:0] pc_next;
  always_comb begin
    if (trap)               pc_next = mtvec;
    else if (mret)          pc_next = mepc;
    else if (jal)           pc_next = instr_addr_o + imm_J;
    else if (jalr)          pc_next = (rd1 + imm_I) & ~32'b1;
    else if (branch && alu_flag) pc_next = instr_addr_o + imm_B;
    else                    pc_next = instr_addr_o + 32'd4;
  end

  always_ff @(posedge clk_i) begin
    if (rst_i) begin
      instr_addr_o <= 32'b0;
    end else if (!stall_i) begin
      instr_addr_o <= pc_next;
    end
  end

endmodule
