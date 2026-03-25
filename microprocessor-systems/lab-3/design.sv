// lab1_adders.sv и lab2_alu.sv подключаются при компиляции как исторические зависимости.
// Компиляция: iverilog -g2012 -o sim memory_pkg.sv design.sv testbench.sv && vvp sim

// ============================================================
// Лабораторная работа №3 — Память инструкций
// Код предоставлен в методичке в готовом виде
// ============================================================
module instr_mem
  import memory_pkg::INSTR_MEM_SIZE_BYTES;
  import memory_pkg::INSTR_MEM_SIZE_WORDS;
(
  input  logic [31:0] read_addr_i,
  output logic [31:0] read_data_o
);
  logic [31:0] ROM [INSTR_MEM_SIZE_WORDS];

  initial begin
    $readmemh("program.mem", ROM);
  end

  assign read_data_o = ROM[read_addr_i[$clog2(INSTR_MEM_SIZE_BYTES)-1:2]];

endmodule

// ============================================================
// Лабораторная работа №3 — Регистровый файл
// 32 регистра × 32 бита, 2 порта чтения (асинхр.), 1 порт записи (синхр.)
// Регистр 0 — аппаратный ноль (запись запрещена, чтение всегда 0)
// ============================================================
module register_file (
  input  logic        clk_i,
  input  logic        write_enable_i,

  input  logic [ 4:0] write_addr_i,
  input  logic [ 4:0] read_addr1_i,
  input  logic [ 4:0] read_addr2_i,

  input  logic [31:0] write_data_i,
  output logic [31:0] read_data1_o,
  output logic [31:0] read_data2_o
);
  logic [31:0] rf_mem [0:31];

  // Запись: синхронная, запрет записи в регистр 0
  always_ff @(posedge clk_i) begin
    if (write_enable_i && write_addr_i != 5'd0)
      rf_mem[write_addr_i] <= write_data_i;
  end

  // Чтение: асинхронное, регистр 0 всегда возвращает 0
  assign read_data1_o = (read_addr1_i == 5'd0) ? 32'd0 : rf_mem[read_addr1_i];
  assign read_data2_o = (read_addr2_i == 5'd0) ? 32'd0 : rf_mem[read_addr2_i];

endmodule
