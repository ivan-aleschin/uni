`timescale 1ns/1ps

module testbench;
  import decoder_pkg::*;

  logic [31:0] fetched_instr_i;

  logic [1:0] a_sel_o;
  logic [2:0] b_sel_o;
  logic [4:0] alu_op_o;
  logic [2:0] csr_op_o;
  logic       csr_we_o;
  logic       mem_req_o;
  logic       mem_we_o;
  logic [2:0] mem_size_o;
  logic       gpr_we_o;
  logic [1:0] wb_sel_o;
  logic       illegal_instr_o;
  logic       branch_o;
  logic       jal_o;
  logic       jalr_o;
  logic       mret_o;

  decoder dut (
    .fetched_instr_i (fetched_instr_i),
    .a_sel_o         (a_sel_o),
    .b_sel_o         (b_sel_o),
    .alu_op_o        (alu_op_o),
    .csr_op_o        (csr_op_o),
    .csr_we_o        (csr_we_o),
    .mem_req_o       (mem_req_o),
    .mem_we_o        (mem_we_o),
    .mem_size_o      (mem_size_o),
    .gpr_we_o        (gpr_we_o),
    .wb_sel_o        (wb_sel_o),
    .illegal_instr_o (illegal_instr_o),
    .branch_o        (branch_o),
    .jal_o           (jal_o),
    .jalr_o          (jalr_o),
    .mret_o          (mret_o)
  );

  task automatic show(string label);
    $display("%s instr=%h illegal=%0b a_sel=%0d b_sel=%0d alu=%0d csr_op=%0d csr_we=%0b mem_req=%0b mem_we=%0b mem_size=%0d gpr_we=%0b wb_sel=%0d br=%0b jal=%0b jalr=%0b mret=%0b",
      label, fetched_instr_i, illegal_instr_o, a_sel_o, b_sel_o, alu_op_o, csr_op_o, csr_we_o,
      mem_req_o, mem_we_o, mem_size_o, gpr_we_o, wb_sel_o, branch_o, jal_o, jalr_o, mret_o);
  endtask

  initial begin
    // ADD x1,x2,x3 -> opcode OP, func3=000, func7=0000000
    fetched_instr_i = {7'h00, 5'd3, 5'd2, 3'h0, 5'd1, OP_OPCODE, 2'b11};
    #1; show("ADD");

    // ADDI x1,x2,5 -> opcode OP_IMM, func3=000
    fetched_instr_i = {12'd5, 5'd2, 3'h0, 5'd1, OP_IMM_OPCODE, 2'b11};
    #1; show("ADDI");

    // LW x1, 0(x2) -> opcode LOAD, func3=010
    fetched_instr_i = {12'd0, 5'd2, 3'h2, 5'd1, LOAD_OPCODE, 2'b11};
    #1; show("LW");

    // SW x3, 0(x2) -> opcode STORE, func3=010
    fetched_instr_i = {7'd0, 5'd3, 5'd2, 3'h2, 5'd0, STORE_OPCODE, 2'b11};
    #1; show("SW");

    // BEQ x1,x2,imm -> opcode BRANCH, func3=000
    fetched_instr_i = {1'b0, 6'd0, 5'd2, 5'd1, 3'h0, 4'd0, 1'b0, BRANCH_OPCODE, 2'b11};
    #1; show("BEQ");

    // JAL x1, imm -> opcode JAL
    fetched_instr_i = {1'b0, 10'd0, 1'b0, 8'd0, 5'd1, JAL_OPCODE, 2'b11};
    #1; show("JAL");

    // JALR x1, 0(x2) -> opcode JALR, func3=000
    fetched_instr_i = {12'd0, 5'd2, 3'h0, 5'd1, JALR_OPCODE, 2'b11};
    #1; show("JALR");

    // LUI x1, imm -> opcode LUI
    fetched_instr_i = {20'h12345, 5'd1, LUI_OPCODE, 2'b11};
    #1; show("LUI");

    // AUIPC x1, imm -> opcode AUIPC
    fetched_instr_i = {20'h12345, 5'd1, AUIPC_OPCODE, 2'b11};
    #1; show("AUIPC");

    // CSRRW x1, csr, x2 -> opcode SYSTEM, func3=001
    fetched_instr_i = {12'h300, 5'd2, 3'h1, 5'd1, SYSTEM_OPCODE, 2'b11};
    #1; show("CSRRW");

    // MRET
    fetched_instr_i = 32'h3020_0073;
    #1; show("MRET");

    // Illegal (bad low bits)
    fetched_instr_i = {7'h00, 5'd0, 5'd0, 3'h0, 5'd0, OP_OPCODE, 2'b10};
    #1; show("ILLEGAL");

    $finish;
  end

endmodule
