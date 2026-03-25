// ============================================================
// Лабораторная работа №4 — Простейшее программируемое устройство
// Архитектура CYBERcobra 3000 Pro 2.1
// ============================================================

// ============================================================
// Память инструкций (ПЗУ), асинхронное чтение
// ============================================================
module instr_mem (
  input  logic [31:0] read_addr_i,
  output logic [31:0] read_data_o
);
  import memory_pkg::INSTR_MEM_SIZE_BYTES;
  import memory_pkg::INSTR_MEM_SIZE_WORDS;

  logic [31:0] ROM [0:INSTR_MEM_SIZE_WORDS-1];

  initial begin
    $readmemh("program.mem", ROM);
  end

  // побайтовая адресация: индекс слова = addr[log2(bytes)-1 : 2]
  assign read_data_o = ROM[read_addr_i[$clog2(INSTR_MEM_SIZE_BYTES)-1:2]];
endmodule

// ============================================================
// Регистровый файл: 32×32, 2 порта чтения (асинхр), 1 порт записи (синхр)
// Регистр 0 всегда равен 0
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

  always_ff @(posedge clk_i) begin
    if (write_enable_i && write_addr_i != 5'd0)
      rf_mem[write_addr_i] <= write_data_i;
  end

  assign read_data1_o = (read_addr1_i == 5'd0) ? 32'd0 : rf_mem[read_addr1_i];
  assign read_data2_o = (read_addr2_i == 5'd0) ? 32'd0 : rf_mem[read_addr2_i];
endmodule

// ============================================================
// Процессор CYBERcobra
// ============================================================
module CYBERcobra (
  input  logic         clk_i,
  input  logic         rst_i,
  input  logic [15:0]  sw_i,
  output logic [31:0]  out_o
);

  // ----------------------------
  // PC
  // ----------------------------
  logic [31:0] pc_q;

  // ----------------------------
  // Инструкция
  // ----------------------------
  logic [31:0] instr;

  // Поля инструкции
  logic        bit_j;
  logic        bit_b;
  logic [1:0]  ws;
  logic [4:0]  alu_op;
  logic [4:0]  ra1;
  logic [4:0]  ra2;
  logic [4:0]  wa;
  logic [22:0] rf_const_raw;
  logic [7:0]  offset_raw;

  // ----------------------------
  // Регистровый файл
  // ----------------------------
  logic [31:0] rf_rd1;
  logic [31:0] rf_rd2;
  logic [31:0] rf_wd;
  logic        rf_we;

  // ----------------------------
  // АЛУ
  // ----------------------------
  logic [31:0] alu_result;
  logic        alu_flag;

  // ----------------------------
  // PC adder
  // ----------------------------
  logic [31:0] pc_addend;
  logic [31:0] pc_sum;

  // ----------------------------
  // Декодирование полей
  // ----------------------------
  assign bit_j       = instr[31];
  assign bit_b       = instr[30];
  assign ws          = instr[29:28];
  assign alu_op      = instr[27:23];
  assign ra1         = instr[22:18];
  assign ra2         = instr[17:13];
  assign offset_raw  = instr[12:5];
  assign wa          = instr[4:0];
  assign rf_const_raw= instr[27:5];

  // ----------------------------
  // Знакорасширения
  // ----------------------------
  logic [31:0] rf_const_sext;
  logic [31:0] offset_sext_shift2;

  assign rf_const_sext      = {{9{rf_const_raw[22]}}, rf_const_raw};
  assign offset_sext_shift2 = {{22{offset_raw[7]}}, offset_raw, 2'b00};

  // ----------------------------
  // Выбор источника записи в RF
  // WS: 0-const, 1-ALU, 2-sw_i, 3-не используется
  // ----------------------------
  always_comb begin
    case (ws)
      2'b00: rf_wd = rf_const_sext;
      2'b01: rf_wd = alu_result;
      2'b10: rf_wd = {16'd0, sw_i};
      default: rf_wd = 32'd0;
    endcase
  end

  // ----------------------------
  // Логика записи в RF
  // ----------------------------
  assign rf_we = ~(bit_b | bit_j);

  // ----------------------------
  // Логика обновления PC
  // ----------------------------
  logic take_branch_or_jump;
  assign take_branch_or_jump = bit_j | (bit_b & alu_flag);

  always_comb begin
    pc_addend = take_branch_or_jump ? offset_sext_shift2 : 32'd4;
  end

  // ----------------------------
  // Инстансы модулей
  // ----------------------------
  instr_mem imem (
    .read_addr_i(pc_q),
    .read_data_o(instr)
  );

  register_file rf (
    .clk_i         (clk_i),
    .write_enable_i(rf_we),
    .write_addr_i  (wa),
    .read_addr1_i  (ra1),
    .read_addr2_i  (ra2),
    .write_data_i  (rf_wd),
    .read_data1_o  (rf_rd1),
    .read_data2_o  (rf_rd2)
  );

  alu alu0 (
    .alu_op_i(alu_op),
    .a_i     (rf_rd1),
    .b_i     (rf_rd2),
    .result_o(alu_result),
    .flag_o  (alu_flag)
  );

  fulladder32 pc_adder (
    .a_i     (pc_q),
    .b_i     (pc_addend),
    .carry_i (1'b0),
    .sum_o   (pc_sum),
    .carry_o ()
  );

  // ----------------------------
  // PC регистр
  // ----------------------------
  always_ff @(posedge clk_i) begin
    if (rst_i)
      pc_q <= 32'd0;
    else
      pc_q <= pc_sum;
  end

  // ----------------------------
  // Вывод
  // ----------------------------
  assign out_o = rf_rd1;

endmodule
