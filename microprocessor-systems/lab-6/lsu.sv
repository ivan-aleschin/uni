/* -----------------------------------------------------------------------------
* Project Name   : Architectures of Processor Systems (APS) lab work
* Organization   : National Research University of Electronic Technology (MIET)
* Department     : Institute of Microdevices and Control Systems
* Author(s)      : Andrei Solodovnikov
* Email(s)       : hepoh@org.miet.ru
* ------------------------------------------------------------------------------
*/
module lsu (
  input  logic        clk_i,
  input  logic        rst_i,

  // Interface with Core
  input  logic [31:0] addr_i,
  input  logic [31:0] wd_i,
  input  logic [ 2:0] size_i,
  input  logic        req_i,
  input  logic        we_i,
  output logic [31:0] rd_o,
  output logic        stall_o,

  // Interface with Memory
  output logic [31:0] mem_addr_o,
  output logic [31:0] mem_wd_o,
  output logic        mem_we_o,
  output logic [ 3:0] mem_be_o, // Byte enables
  output logic        mem_req_o,
  input  logic [31:0] mem_rd_i
);

  import decoder_pkg::*;

  // Логика Stall: на 1 такт при любом запросе в память
  logic stall_q;
  always_ff @(posedge clk_i) begin
    if (rst_i) stall_q <= 1'b0;
    else       stall_q <= req_i && !stall_q;
  end
  assign stall_o = req_i && !stall_q;

  assign mem_addr_o = {addr_i[31:2], 2'b00};
  assign mem_req_o  = req_i;
  assign mem_we_o   = we_i && !stall_q;

  // Подготовка данных для записи (Store)
  always_comb begin
    mem_wd_o = wd_i;
    mem_be_o = 4'b0000;
    if (we_i) begin
      case (size_i)
        LDST_B: begin
          mem_be_o = 4'b0001 << addr_i[1:0];
          mem_wd_o = {4{wd_i[7:0]}};
        end
        LDST_H: begin
          mem_be_o = addr_i[1] ? 4'b1100 : 4'b0011;
          mem_wd_o = {2{wd_i[15:0]}};
        end
        LDST_W: begin
          mem_be_o = 4'b1111;
          mem_wd_o = wd_i;
        end
      endcase
    end
  end

  // Обработка считанных данных (Load)
  logic [ 7:0] byte_data;
  logic [15:0] half_data;

  assign byte_data = mem_rd_i[8*addr_i[1:0] +: 8];
  assign half_data = addr_i[1] ? mem_rd_i[31:16] : mem_rd_i[15:0];

  always_comb begin
    case (size_i)
      LDST_B:  rd_o = {{24{byte_data[7]}}, byte_data};
      LDST_H:  rd_o = {{16{half_data[15]}}, half_data};
      LDST_W:  rd_o = mem_rd_i;
      LDST_BU: rd_o = {24'b0, byte_data};
      LDST_HU: rd_o = {16'b0, half_data};
      default: rd_o = mem_rd_i;
    endcase
  end

endmodule
