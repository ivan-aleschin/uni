/* -----------------------------------------------------------------------------
* Project Name   : Architectures of Processor Systems (APS) lab work
* Organization   : National Research University of Electronic Technology (MIET)
* Department     : Institute of Microdevices and Control Systems
* Author(s)      : Andrei Solodovnikov
* Email(s)       : hepoh@org.miet.ru

See https://github.com/MPSU/APS/blob/master/LICENSE file for licensing details.
* ------------------------------------------------------------------------------
*/
module instr_mem (
  input  logic [31:0] addr_i,
  output logic [31:0] read_data_o
);
  import memory_pkg::INSTR_MEM_SIZE_BYTES;
  import memory_pkg::INSTR_MEM_SIZE_WORDS;

  logic [31:0] ROM [0:INSTR_MEM_SIZE_WORDS-1];

  initial begin
    $readmemh("program.mem", ROM);
  end

  // побайтовая адресация: индекс слова = addr[log2(bytes)-1 : 2]
  assign read_data_o = ROM[addr_i[$clog2(INSTR_MEM_SIZE_BYTES)-1:2]];

endmodule
