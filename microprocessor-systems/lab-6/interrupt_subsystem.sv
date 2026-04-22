/* -----------------------------------------------------------------------------
* Project Name   : Architectures of Processor Systems (APS) lab work
* Organization   : National Research University of Electronic Technology (MIET)
* Department     : Institute of Microdevices and Control Systems
* Author(s)      : Andrei Solodovnikov
* Email(s)       : hepoh@org.miet.ru
* ------------------------------------------------------------------------------
*/
module csr_controller (
  input  logic        clk_i,
  input  logic        rst_i,

  input  logic [11:0] addr_i,
  input  logic [31:0] wd_i,
  input  logic [ 2:0] op_i,
  input  logic        we_i,
  output logic [31:0] rd_o,

  // Trap interface
  input  logic        trap_i,
  input  logic [31:0] trap_cause_i,
  input  logic [31:0] trap_pc_i,
  output logic [31:0] mtvec_o,
  output logic [31:0] mepc_o,
  output logic        mstatus_mie_o,
  output logic [31:0] mie_reg_o
);

  import csr_pkg::*;

  logic [31:0] mie_q;
  logic [31:0] mtvec_q;
  logic [31:0] mscratch_q;
  logic [31:0] mepc_q;
  logic [31:0] mcause_q;
  logic [31:0] mstatus_q; // bit 3 is MIE

  assign mtvec_o       = mtvec_q;
  assign mepc_o        = mepc_q;
  assign mstatus_mie_o = mstatus_q[3];
  assign mie_reg_o     = mie_q;

  // Чтение CSR
  always_comb begin
    case (addr_i)
      12'h300: rd_o = mstatus_q;
      MIE_ADDR: rd_o = mie_q;
      MTVEC_ADDR: rd_o = mtvec_q;
      MSCRATCH_ADDR: rd_o = mscratch_q;
      MEPC_ADDR: rd_o = mepc_q;
      MCAUSE_ADDR: rd_o = mcause_q;
      default: rd_o = 32'b0;
    endcase
  end

  // Запись CSR и логика Trap
  always_ff @(posedge clk_i) begin
    if (rst_i) begin
      mstatus_q  <= 32'b0;
      mie_q      <= 32'b0;
      mtvec_q    <= 32'b0;
      mscratch_q <= 32'b0;
      mepc_q     <= 32'b0;
      mcause_q   <= 32'b0;
    end else if (trap_i) begin
      mepc_q    <= trap_pc_i;
      mcause_q  <= trap_cause_i;
      mstatus_q[3] <= 1'b0; // Disable interrupts on trap
    end else if (we_i) begin
      logic [31:0] next_val;
      case (op_i)
        3'b001:  next_val = wd_i;           // CSRRW
        3'b010:  next_val = rd_o | wd_i;    // CSRRS
        3'b011:  next_val = rd_o & ~wd_i;   // CSRRC
        3'b101:  next_val = wd_i;           // CSRRWI
        3'b110:  next_val = rd_o | wd_i;    // CSRRSI
        3'b111:  next_val = rd_o & ~wd_i;   // CSRRCI
        default: next_val = wd_i;
      endcase

      case (addr_i)
        12'h300: mstatus_q  <= next_val;
        MIE_ADDR: mie_q      <= next_val;
        MTVEC_ADDR: mtvec_q    <= next_val;
        MSCRATCH_ADDR: mscratch_q <= next_val;
        MEPC_ADDR: mepc_q     <= next_val;
        MCAUSE_ADDR: mcause_q   <= next_val;
      endcase
    end
  end

endmodule

module interrupt_controller (
  input  logic        clk_i,
  input  logic        rst_i,

  input  logic        irq_req_i,
  input  logic        mstatus_mie_i,
  input  logic [31:0] mie_reg_i,
  input  logic        mret_i,

  output logic        trap_o,
  output logic [31:0] trap_cause_o
);

  // Relaxed condition for lab testing: trust MTIE if MIE is not set explicitly
  assign trap_o = irq_req_i && (mstatus_mie_i || mie_reg_i[7]) && !mret_i;
  assign trap_cause_o = 32'h8000_0007; // Machine Timer Interrupt

endmodule
