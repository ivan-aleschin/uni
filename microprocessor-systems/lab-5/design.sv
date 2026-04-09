module decoder (
  input  logic [31:0]  fetched_instr_i,
  output logic [1:0]   a_sel_o,
  output logic [2:0]   b_sel_o,
  output logic [4:0]   alu_op_o,
  output logic [2:0]   csr_op_o,
  output logic         csr_we_o,
  output logic         mem_req_o,
  output logic         mem_we_o,
  output logic [2:0]   mem_size_o,
  output logic         gpr_we_o,
  output logic [1:0]   wb_sel_o,
  output logic         illegal_instr_o,
  output logic         branch_o,
  output logic         jal_o,
  output logic         jalr_o,
  output logic         mret_o
);
  import decoder_pkg::*;

  logic [4:0] opcode;
  logic [2:0] func3;
  logic [6:0] func7;
  logic [1:0] low_bits;

  assign opcode   = fetched_instr_i[6:2];
  assign func3    = fetched_instr_i[14:12];
  assign func7    = fetched_instr_i[31:25];
  assign low_bits = fetched_instr_i[1:0];

  always_comb begin
    // defaults -> illegal / no side effects
    a_sel_o         = OP_A_RS1;
    b_sel_o         = OP_B_RS2;
    alu_op_o        = ALU_ADD;
    csr_op_o        = 3'b000;
    csr_we_o        = 1'b0;
    mem_req_o       = 1'b0;
    mem_we_o        = 1'b0;
    mem_size_o      = 3'b011;
    gpr_we_o        = 1'b0;
    wb_sel_o        = WB_EX_RESULT;
    illegal_instr_o = 1'b1;
    branch_o        = 1'b0;
    jal_o           = 1'b0;
    jalr_o          = 1'b0;
    mret_o          = 1'b0;

    if (low_bits == 2'b11) begin
      case (opcode)
        OP_OPCODE: begin
          a_sel_o         = OP_A_RS1;
          b_sel_o         = OP_B_RS2;
          wb_sel_o        = WB_EX_RESULT;
          gpr_we_o        = 1'b1;
          illegal_instr_o = 1'b0;
          case (func3)
            3'h0: begin
              if (func7 == 7'h00) alu_op_o = ALU_ADD;
              else if (func7 == 7'h20) alu_op_o = ALU_SUB;
              else illegal_instr_o = 1'b1;
            end
            3'h1: begin
              if (func7 == 7'h00) alu_op_o = ALU_SLL;
              else illegal_instr_o = 1'b1;
            end
            3'h2: begin
              if (func7 == 7'h00) alu_op_o = ALU_SLTS;
              else illegal_instr_o = 1'b1;
            end
            3'h3: begin
              if (func7 == 7'h00) alu_op_o = ALU_SLTU;
              else illegal_instr_o = 1'b1;
            end
            3'h4: begin
              if (func7 == 7'h00) alu_op_o = ALU_XOR;
              else illegal_instr_o = 1'b1;
            end
            3'h5: begin
              if (func7 == 7'h00) alu_op_o = ALU_SRL;
              else if (func7 == 7'h20) alu_op_o = ALU_SRA;
              else illegal_instr_o = 1'b1;
            end
            3'h6: begin
              if (func7 == 7'h00) alu_op_o = ALU_OR;
              else illegal_instr_o = 1'b1;
            end
            3'h7: begin
              if (func7 == 7'h00) alu_op_o = ALU_AND;
              else illegal_instr_o = 1'b1;
            end
            default: illegal_instr_o = 1'b1;
          endcase
        end

        OP_IMM_OPCODE: begin
          a_sel_o         = OP_A_RS1;
          b_sel_o         = OP_B_IMM_I;
          wb_sel_o        = WB_EX_RESULT;
          gpr_we_o        = 1'b1;
          illegal_instr_o = 1'b0;
          case (func3)
            3'h0: begin
              alu_op_o = ALU_ADD;
            end
            3'h1: begin
              if (func7 == 7'h00) alu_op_o = ALU_SLL;
              else illegal_instr_o = 1'b1;
            end
            3'h2: begin
              alu_op_o = ALU_SLTS;
            end
            3'h3: begin
              alu_op_o = ALU_SLTU;
            end
            3'h4: begin
              alu_op_o = ALU_XOR;
            end
            3'h5: begin
              if (func7 == 7'h00) alu_op_o = ALU_SRL;
              else if (func7 == 7'h20) alu_op_o = ALU_SRA;
              else illegal_instr_o = 1'b1;
            end
            3'h6: begin
              alu_op_o = ALU_OR;
            end
            3'h7: begin
              alu_op_o = ALU_AND;
            end
            default: illegal_instr_o = 1'b1;
          endcase
        end

        LOAD_OPCODE: begin
          a_sel_o         = OP_A_RS1;
          b_sel_o         = OP_B_IMM_I;
          alu_op_o        = ALU_ADD;
          mem_req_o       = 1'b1;
          mem_we_o        = 1'b0;
          wb_sel_o        = WB_LSU_DATA;
          gpr_we_o        = 1'b1;
          illegal_instr_o = 1'b0;
          case (func3)
            3'h0: mem_size_o = LDST_B;
            3'h1: mem_size_o = LDST_H;
            3'h2: mem_size_o = LDST_W;
            3'h4: mem_size_o = LDST_BU;
            3'h5: mem_size_o = LDST_HU;
            default: illegal_instr_o = 1'b1;
          endcase
        end

        STORE_OPCODE: begin
          a_sel_o         = OP_A_RS1;
          b_sel_o         = OP_B_IMM_S;
          alu_op_o        = ALU_ADD;
          mem_req_o       = 1'b1;
          mem_we_o        = 1'b1;
          gpr_we_o        = 1'b0;
          wb_sel_o        = WB_EX_RESULT;
          illegal_instr_o = 1'b0;
          case (func3)
            3'h0: mem_size_o = LDST_B;
            3'h1: mem_size_o = LDST_H;
            3'h2: mem_size_o = LDST_W;
            default: illegal_instr_o = 1'b1;
          endcase
        end

        BRANCH_OPCODE: begin
          a_sel_o         = OP_A_RS1;
          b_sel_o         = OP_B_RS2;
          branch_o        = 1'b1;
          gpr_we_o        = 1'b0;
          wb_sel_o        = WB_EX_RESULT;
          illegal_instr_o = 1'b0;
          case (func3)
            3'h0: alu_op_o = ALU_EQ;
            3'h1: alu_op_o = ALU_NE;
            3'h4: alu_op_o = ALU_LTS;
            3'h5: alu_op_o = ALU_GES;
            3'h6: alu_op_o = ALU_LTU;
            3'h7: alu_op_o = ALU_GEU;
            default: illegal_instr_o = 1'b1;
          endcase
        end

        JAL_OPCODE: begin
          a_sel_o         = OP_A_CURR_PC;
          b_sel_o         = OP_B_INCR;
          alu_op_o        = ALU_ADD;
          jal_o           = 1'b1;
          gpr_we_o        = 1'b1;
          wb_sel_o        = WB_EX_RESULT;
          illegal_instr_o = 1'b0;
        end

        JALR_OPCODE: begin
          a_sel_o         = OP_A_CURR_PC;
          b_sel_o         = OP_B_INCR;
          alu_op_o        = ALU_ADD;
          jalr_o          = 1'b1;
          gpr_we_o        = 1'b1;
          wb_sel_o        = WB_EX_RESULT;
          illegal_instr_o = 1'b0;
          if (func3 != 3'h0) illegal_instr_o = 1'b1;
        end

        LUI_OPCODE: begin
          a_sel_o         = OP_A_ZERO;
          b_sel_o         = OP_B_IMM_U;
          alu_op_o        = ALU_ADD;
          gpr_we_o        = 1'b1;
          wb_sel_o        = WB_EX_RESULT;
          illegal_instr_o = 1'b0;
        end

        AUIPC_OPCODE: begin
          a_sel_o         = OP_A_CURR_PC;
          b_sel_o         = OP_B_IMM_U;
          alu_op_o        = ALU_ADD;
          gpr_we_o        = 1'b1;
          wb_sel_o        = WB_EX_RESULT;
          illegal_instr_o = 1'b0;
        end

        MISC_MEM_OPCODE: begin
          a_sel_o         = OP_A_RS1;
          b_sel_o         = OP_B_RS2;
          alu_op_o        = ALU_ADD;
          gpr_we_o        = 1'b0;
          wb_sel_o        = WB_EX_RESULT;
          illegal_instr_o = (func3 != 3'h0);
        end

        SYSTEM_OPCODE: begin
          a_sel_o   = OP_A_RS1;
          b_sel_o   = OP_B_RS2;
          alu_op_o  = ALU_ADD;
          wb_sel_o  = WB_CSR_DATA;
          gpr_we_o  = 1'b1;
          csr_we_o  = 1'b1;
          illegal_instr_o = 1'b0;

          case (func3)
            3'h0: begin
              // ECALL/EBREAK/MRET: full instruction match
              gpr_we_o = 1'b0;
              csr_we_o = 1'b0;
              wb_sel_o = WB_EX_RESULT;
              if (fetched_instr_i == 32'h3020_0073) begin
                mret_o          = 1'b1;
                illegal_instr_o = 1'b0;
              end else if ((fetched_instr_i == 32'h0000_0073) || (fetched_instr_i == 32'h0010_0073)) begin
                illegal_instr_o = 1'b1;
              end else begin
                illegal_instr_o = 1'b1;
              end
            end
            3'h1, 3'h2, 3'h3, 3'h5, 3'h6, 3'h7: begin
              csr_op_o        = func3;
              csr_we_o        = 1'b1;
              gpr_we_o        = 1'b1;
              wb_sel_o        = WB_CSR_DATA;
              illegal_instr_o = 1'b0;
            end
            default: begin
              csr_we_o        = 1'b0;
              gpr_we_o        = 1'b0;
              wb_sel_o        = WB_EX_RESULT;
              illegal_instr_o = 1'b1;
            end
          endcase
        end

        default: begin
          // keep defaults (illegal)
        end
      endcase
    end

    if (illegal_instr_o) begin
      csr_we_o  = 1'b0;
      mem_req_o = 1'b0;
      mem_we_o  = 1'b0;
      gpr_we_o  = 1'b0;
      branch_o  = 1'b0;
      jal_o     = 1'b0;
      jalr_o    = 1'b0;
      mret_o    = 1'b0;
    end
  end

endmodule
