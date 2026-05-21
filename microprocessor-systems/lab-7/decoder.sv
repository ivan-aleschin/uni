`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 04/08/2026 10:15:43 PM
// Design Name: 
// Module Name: decoder
// Project Name: 
// Target Devices: 
// Tool Versions: 
// Description: 
// 
// Dependencies: 
// 
// Revision:
// Revision 0.01 - File Created
// Additional Comments:
// 
//////////////////////////////////////////////////////////////////////////////////

module decoder (
  input  logic [31:0] fetched_instr_i,
  output logic [1:0]  a_sel_o,
  output logic [2:0]  b_sel_o,
  output logic [4:0]  alu_op_o,
  output logic [2:0]  csr_op_o,
  output logic        csr_we_o,
  output logic        mem_req_o,
  output logic        mem_we_o,
  output logic [2:0]  mem_size_o,
  output logic        gpr_we_o,
  output logic [1:0]  wb_sel_o,
  output logic        illegal_instr_o,
  output logic        branch_o,
  output logic        jal_o,
  output logic        jalr_o,
  output logic        mret_o
);
  import decoder_pkg::*;

  logic [4:0] opcode;
  logic [2:0] func3;
  logic [6:0] func7;

  assign opcode = fetched_instr_i[6:2];
  assign func3  = fetched_instr_i[14:12];
  assign func7  = fetched_instr_i[31:25];

  always_comb begin
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
    illegal_instr_o = 1'b0;
    branch_o        = 1'b0;
    jal_o           = 1'b0;
    jalr_o          = 1'b0;
    mret_o          = 1'b0;

    if (fetched_instr_i[1:0] != 2'b11) begin
      illegal_instr_o = 1'b1;
    end else begin
      unique case (opcode)
        LUI_OPCODE: begin
          a_sel_o  = OP_A_ZERO;
          b_sel_o  = OP_B_IMM_U;
          alu_op_o = ALU_ADD;
          gpr_we_o = 1'b1;
          wb_sel_o = WB_EX_RESULT;
        end

        AUIPC_OPCODE: begin
          a_sel_o  = OP_A_CURR_PC;
          b_sel_o  = OP_B_IMM_U;
          alu_op_o = ALU_ADD;
          gpr_we_o = 1'b1;
          wb_sel_o = WB_EX_RESULT;
        end

        JAL_OPCODE: begin
          a_sel_o  = OP_A_CURR_PC;
          b_sel_o  = OP_B_INCR;
          alu_op_o = ALU_ADD;
          gpr_we_o = 1'b1;
          wb_sel_o = WB_EX_RESULT;
          jal_o    = 1'b1;
        end

        JALR_OPCODE: begin
          if (func3 == 3'b000) begin
            a_sel_o  = OP_A_CURR_PC;
            b_sel_o  = OP_B_INCR;
            alu_op_o = ALU_ADD;
            gpr_we_o = 1'b1;
            wb_sel_o = WB_EX_RESULT;
            jalr_o   = 1'b1;
          end else begin
            illegal_instr_o = 1'b1;
          end
        end

        BRANCH_OPCODE: begin
          case (func3)
            3'b000: begin branch_o = 1'b1; a_sel_o = OP_A_RS1; b_sel_o = OP_B_RS2; alu_op_o = ALU_EQ;  end
            3'b001: begin branch_o = 1'b1; a_sel_o = OP_A_RS1; b_sel_o = OP_B_RS2; alu_op_o = ALU_NE;  end
            3'b100: begin branch_o = 1'b1; a_sel_o = OP_A_RS1; b_sel_o = OP_B_RS2; alu_op_o = ALU_LTS; end
            3'b101: begin branch_o = 1'b1; a_sel_o = OP_A_RS1; b_sel_o = OP_B_RS2; alu_op_o = ALU_GES; end
            3'b110: begin branch_o = 1'b1; a_sel_o = OP_A_RS1; b_sel_o = OP_B_RS2; alu_op_o = ALU_LTU; end
            3'b111: begin branch_o = 1'b1; a_sel_o = OP_A_RS1; b_sel_o = OP_B_RS2; alu_op_o = ALU_GEU; end
            default: illegal_instr_o = 1'b1;
          endcase
        end

        LOAD_OPCODE: begin
          case (func3)
            3'b000: begin
              a_sel_o   = OP_A_RS1;
              b_sel_o   = OP_B_IMM_I;
              alu_op_o  = ALU_ADD;
              mem_req_o = 1'b1;
              mem_size_o= LDST_B;
              gpr_we_o  = 1'b1;
              wb_sel_o  = WB_LSU_DATA;
            end
            3'b001: begin
              a_sel_o   = OP_A_RS1;
              b_sel_o   = OP_B_IMM_I;
              alu_op_o  = ALU_ADD;
              mem_req_o = 1'b1;
              mem_size_o= LDST_H;
              gpr_we_o  = 1'b1;
              wb_sel_o  = WB_LSU_DATA;
            end
            3'b010: begin
              a_sel_o   = OP_A_RS1;
              b_sel_o   = OP_B_IMM_I;
              alu_op_o  = ALU_ADD;
              mem_req_o = 1'b1;
              mem_size_o= LDST_W;
              gpr_we_o  = 1'b1;
              wb_sel_o  = WB_LSU_DATA;
            end
            3'b100: begin
              a_sel_o   = OP_A_RS1;
              b_sel_o   = OP_B_IMM_I;
              alu_op_o  = ALU_ADD;
              mem_req_o = 1'b1;
              mem_size_o= LDST_BU;
              gpr_we_o  = 1'b1;
              wb_sel_o  = WB_LSU_DATA;
            end
            3'b101: begin
              a_sel_o   = OP_A_RS1;
              b_sel_o   = OP_B_IMM_I;
              alu_op_o  = ALU_ADD;
              mem_req_o = 1'b1;
              mem_size_o= LDST_HU;
              gpr_we_o  = 1'b1;
              wb_sel_o  = WB_LSU_DATA;
            end
            default: illegal_instr_o = 1'b1;
          endcase
        end

        STORE_OPCODE: begin
          case (func3)
            3'b000: begin
              a_sel_o    = OP_A_RS1;
              b_sel_o    = OP_B_IMM_S;
              alu_op_o   = ALU_ADD;
              mem_req_o  = 1'b1;
              mem_we_o   = 1'b1;
              mem_size_o = LDST_B;
            end
            3'b001: begin
              a_sel_o    = OP_A_RS1;
              b_sel_o    = OP_B_IMM_S;
              alu_op_o   = ALU_ADD;
              mem_req_o  = 1'b1;
              mem_we_o   = 1'b1;
              mem_size_o = LDST_H;
            end
            3'b010: begin
              a_sel_o    = OP_A_RS1;
              b_sel_o    = OP_B_IMM_S;
              alu_op_o   = ALU_ADD;
              mem_req_o  = 1'b1;
              mem_we_o   = 1'b1;
              mem_size_o = LDST_W;
            end
            default: illegal_instr_o = 1'b1;
          endcase
        end

        OP_IMM_OPCODE: begin
          case (func3)
            3'b000: begin a_sel_o = OP_A_RS1; b_sel_o = OP_B_IMM_I; alu_op_o = ALU_ADD;  gpr_we_o = 1'b1; wb_sel_o = WB_EX_RESULT; end
            3'b010: begin a_sel_o = OP_A_RS1; b_sel_o = OP_B_IMM_I; alu_op_o = ALU_SLTS; gpr_we_o = 1'b1; wb_sel_o = WB_EX_RESULT; end
            3'b011: begin a_sel_o = OP_A_RS1; b_sel_o = OP_B_IMM_I; alu_op_o = ALU_SLTU; gpr_we_o = 1'b1; wb_sel_o = WB_EX_RESULT; end
            3'b100: begin a_sel_o = OP_A_RS1; b_sel_o = OP_B_IMM_I; alu_op_o = ALU_XOR;  gpr_we_o = 1'b1; wb_sel_o = WB_EX_RESULT; end
            3'b110: begin a_sel_o = OP_A_RS1; b_sel_o = OP_B_IMM_I; alu_op_o = ALU_OR;   gpr_we_o = 1'b1; wb_sel_o = WB_EX_RESULT; end
            3'b111: begin a_sel_o = OP_A_RS1; b_sel_o = OP_B_IMM_I; alu_op_o = ALU_AND;  gpr_we_o = 1'b1; wb_sel_o = WB_EX_RESULT; end

            3'b001: begin
              if (func7 == 7'h00) begin
                a_sel_o  = OP_A_RS1;
                b_sel_o  = OP_B_IMM_I;
                alu_op_o = ALU_SLL;
                gpr_we_o = 1'b1;
                wb_sel_o = WB_EX_RESULT;
              end else begin
                illegal_instr_o = 1'b1;
              end
            end

            3'b101: begin
              if (func7 == 7'h00) begin
                a_sel_o  = OP_A_RS1;
                b_sel_o  = OP_B_IMM_I;
                alu_op_o = ALU_SRL;
                gpr_we_o = 1'b1;
                wb_sel_o = WB_EX_RESULT;
              end else if (func7 == 7'h20) begin
                a_sel_o  = OP_A_RS1;
                b_sel_o  = OP_B_IMM_I;
                alu_op_o = ALU_SRA;
                gpr_we_o = 1'b1;
                wb_sel_o = WB_EX_RESULT;
              end else begin
                illegal_instr_o = 1'b1;
              end
            end

            default: illegal_instr_o = 1'b1;
          endcase
        end

        OP_OPCODE: begin
          case (func3)
            3'b000: begin
              if (func7 == 7'h00) begin
                a_sel_o  = OP_A_RS1;
                b_sel_o  = OP_B_RS2;
                alu_op_o = ALU_ADD;
                gpr_we_o = 1'b1;
                wb_sel_o = WB_EX_RESULT;
              end else if (func7 == 7'h20) begin
                a_sel_o  = OP_A_RS1;
                b_sel_o  = OP_B_RS2;
                alu_op_o = ALU_SUB;
                gpr_we_o = 1'b1;
                wb_sel_o = WB_EX_RESULT;
              end else begin
                illegal_instr_o = 1'b1;
              end
            end

            3'b001: begin
              if (func7 == 7'h00) begin
                a_sel_o  = OP_A_RS1;
                b_sel_o  = OP_B_RS2;
                alu_op_o = ALU_SLL;
                gpr_we_o = 1'b1;
                wb_sel_o = WB_EX_RESULT;
              end else begin
                illegal_instr_o = 1'b1;
              end
            end

            3'b010: begin
              if (func7 == 7'h00) begin
                a_sel_o  = OP_A_RS1;
                b_sel_o  = OP_B_RS2;
                alu_op_o = ALU_SLTS;
                gpr_we_o = 1'b1;
                wb_sel_o = WB_EX_RESULT;
              end else begin
                illegal_instr_o = 1'b1;
              end
            end

            3'b011: begin
              if (func7 == 7'h00) begin
                a_sel_o  = OP_A_RS1;
                b_sel_o  = OP_B_RS2;
                alu_op_o = ALU_SLTU;
                gpr_we_o = 1'b1;
                wb_sel_o = WB_EX_RESULT;
              end else begin
                illegal_instr_o = 1'b1;
              end
            end

            3'b100: begin
              if (func7 == 7'h00) begin
                a_sel_o  = OP_A_RS1;
                b_sel_o  = OP_B_RS2;
                alu_op_o = ALU_XOR;
                gpr_we_o = 1'b1;
                wb_sel_o = WB_EX_RESULT;
              end else begin
                illegal_instr_o = 1'b1;
              end
            end

            3'b101: begin
              if (func7 == 7'h00) begin
                a_sel_o  = OP_A_RS1;
                b_sel_o  = OP_B_RS2;
                alu_op_o = ALU_SRL;
                gpr_we_o = 1'b1;
                wb_sel_o = WB_EX_RESULT;
              end else if (func7 == 7'h20) begin
                a_sel_o  = OP_A_RS1;
                b_sel_o  = OP_B_RS2;
                alu_op_o = ALU_SRA;
                gpr_we_o = 1'b1;
                wb_sel_o = WB_EX_RESULT;
              end else begin
                illegal_instr_o = 1'b1;
              end
            end

            3'b110: begin
              if (func7 == 7'h00) begin
                a_sel_o  = OP_A_RS1;
                b_sel_o  = OP_B_RS2;
                alu_op_o = ALU_OR;
                gpr_we_o = 1'b1;
                wb_sel_o = WB_EX_RESULT;
              end else begin
                illegal_instr_o = 1'b1;
              end
            end

            3'b111: begin
              if (func7 == 7'h00) begin
                a_sel_o  = OP_A_RS1;
                b_sel_o  = OP_B_RS2;
                alu_op_o = ALU_AND;
                gpr_we_o = 1'b1;
                wb_sel_o = WB_EX_RESULT;
              end else begin
                illegal_instr_o = 1'b1;
              end
            end

            default: illegal_instr_o = 1'b1;
          endcase
        end

        MISC_MEM_OPCODE: begin
          if (func3 != 3'b000) begin
            illegal_instr_o = 1'b1;
          end
        end

        SYSTEM_OPCODE: begin
          case (func3)
            3'b000: begin
              if (fetched_instr_i == 32'h3020_0073) begin
                mret_o = 1'b1;
              end else if ((fetched_instr_i == 32'h0000_0073) ||
                           (fetched_instr_i == 32'h0010_0073)) begin
                illegal_instr_o = 1'b1;
              end else begin
                illegal_instr_o = 1'b1;
              end
            end

            3'b001: begin csr_op_o = CSR_RW;  csr_we_o = 1'b1; gpr_we_o = 1'b1; wb_sel_o = WB_CSR_DATA; end
            3'b010: begin csr_op_o = CSR_RS;  csr_we_o = 1'b1; gpr_we_o = 1'b1; wb_sel_o = WB_CSR_DATA; end
            3'b011: begin csr_op_o = CSR_RC;  csr_we_o = 1'b1; gpr_we_o = 1'b1; wb_sel_o = WB_CSR_DATA; end
            3'b101: begin csr_op_o = CSR_RWI; csr_we_o = 1'b1; gpr_we_o = 1'b1; wb_sel_o = WB_CSR_DATA; end
            3'b110: begin csr_op_o = CSR_RSI; csr_we_o = 1'b1; gpr_we_o = 1'b1; wb_sel_o = WB_CSR_DATA; end
            3'b111: begin csr_op_o = CSR_RCI; csr_we_o = 1'b1; gpr_we_o = 1'b1; wb_sel_o = WB_CSR_DATA; end
            default: illegal_instr_o = 1'b1;
          endcase
        end

        default: begin
          illegal_instr_o = 1'b1;
        end
      endcase
    end
  end
endmodule