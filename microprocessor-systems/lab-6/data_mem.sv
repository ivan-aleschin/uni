/* -----------------------------------------------------------------------------
* Project Name   : Architectures of Processor Systems (APS) lab work
* Organization   : National Research University of Electronic Technology (MIET)
* Department     : Institute of Microdevices and Control Systems
* Author(s)      : Andrei Solodovnikov
* Email(s)       : hepoh@org.miet.ru

See https://github.com/MPSU/APS/blob/master/LICENSE file for licensing details.
* ------------------------------------------------------------------------------
*/
module data_mem (
  input  logic        clk_i,
  input  logic [31:0] addr_i,
  input  logic        we_i,
  input  logic [ 3:0] be_i,
  input  logic [31:0] wd_i,
  output logic [31:0] rd_o
);
  import memory_pkg::DATA_MEM_SIZE_WORDS;
  import memory_pkg::DATA_MEM_SIZE_BYTES;

  logic [31:0] RAM [0:DATA_MEM_SIZE_WORDS-1];

  always_ff @(posedge clk_i) begin
    if (we_i) begin
      if (be_i[0]) RAM[addr_i[$clog2(DATA_MEM_SIZE_BYTES)-1:2]][ 7: 0] <= wd_i[ 7: 0];
      if (be_i[1]) RAM[addr_i[$clog2(DATA_MEM_SIZE_BYTES)-1:2]][15: 8] <= wd_i[15: 8];
      if (be_i[2]) RAM[addr_i[$clog2(DATA_MEM_SIZE_BYTES)-1:2]][23:16] <= wd_i[23:16];
      if (be_i[3]) RAM[addr_i[$clog2(DATA_MEM_SIZE_BYTES)-1:2]][31:24] <= wd_i[31:24];
    end
  end

  assign rd_o = RAM[addr_i[$clog2(DATA_MEM_SIZE_BYTES)-1:2]];

endmodule
