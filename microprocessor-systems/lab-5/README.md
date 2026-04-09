# Лабораторная работа №5 — Декодер инструкций RISC-V

[Теория](THEORY.md)

## Цель
Реализовать на SystemVerilog модуль декодера инструкций для однотактного RISC-V‑процессора и проверить корректность его работы в симуляции.

---

## Структура файлов

```
lab-5/
├── design.sv               # модуль decoder
├── alu_opcodes_pkg.sv      # коды операций АЛУ
├── csr_pkg.sv              # коды операций CSR
├── decoder_pkg.sv          # опкоды и параметры декодера
├── lab_05.tb_decoder.sv    # официальный тест
├── testbench.sv            # локальный smoke-тест
├── THEORY.md               # теория
└── README.md
```

---

## Сигнатура модуля

```
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
endmodule
```

---

## Пайплайн №1 — Локальный smoke-тест (Verilator)

### Шаг 1. Войти в окружение
Запускай из корня репозитория (где лежит `flake.nix`), либо предварительно перейди в корень и используй относительные пути:

```
nix develop
```

### Шаг 2. Быстрый прогон (Verilator)
`nix develop --command verilator --binary --sv --timing -Wall -Wno-fatal --top-module testbench -o simv alu_opcodes_pkg.sv csr_pkg.sv decoder_pkg.sv design.sv testbench.sv && ./simv`

Ожидаемо: несколько строк с раскодированными инструкциями и `illegal=0` для валидных кейсов.

---

## Пайплайн №2 — Официальный тест в Vivado

1. **File → Project → New → RTL Project**
2. **Design Sources**:
   - `design.sv`
   - `alu_opcodes_pkg.sv`
   - `csr_pkg.sv`
   - `decoder_pkg.sv`
3. **Simulation Sources**:
   - `lab_05.tb_decoder.sv`
4. В **Simulation Sources** выбрать `lab_05_tb_decoder` как top.
5. **Run Behavioral Simulation**

Успех — `Number of errors: 0`.

---

## Примечания по симуляторам
- Официальный `lab_05.tb_decoder.sv` требует полноценной поддержки SystemVerilog (рандомизация/классы/SVA), поэтому нужен полнофункциональный симулятор (Vivado или совместимый CLI‑симулятор).
- Verilator подходит для локального smoke‑теста и не заменяет официальный прогон.

---

## Что должно работать
- Декодируются все инструкции RV32I + Zicsr + `mret`.
- Для нелегальных инструкций:
  - `illegal_instr_o = 1`
  - запрет записи в GPR/CSR
  - запрет обращения к памяти
  - запрет переходов (`branch/jal/jalr/mret = 0`).

---

## Что показывать на защите
- Скриншот/лог симуляции с `Number of errors: 0`
- Готовый модуль `decoder` в `design.sv`
- Краткое объяснение, как формируются управляющие сигналы