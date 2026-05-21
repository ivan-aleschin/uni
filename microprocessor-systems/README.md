# Микропроцессорные средства и системы — Лабораторные работы

Лабораторные работы по курсу «Архитектуры процессорных систем» (МИЭТ). Язык — **SystemVerilog**, симуляция — **iverilog** + **GTKWave**, синтез/прошивка — **Vivado** (Nexys A7-100T).

Официальные материалы: [репозиторий APS](https://github.com/MPSU/APS) → [Labs/](https://github.com/MPSU/APS/tree/master/Labs)

---

## Содержание

| Папка | Оригинал | Описание |
|---|---|---|
| `lab-1/` | ЛР1 | Сумматор (Adder) |
| `lab-2/` | ЛР2 | Арифметико-логическое устройство (ALU) |
| `lab-3/` | ЛР3 | Регистровый файл и память инструкций |
| `lab-4/` | ЛР4 | Простейшее программируемое устройство (CYBERcobra) |
| `lab-5/` | ЛР5 | Декодер инструкций RISC-V |
| `lab-6/` | ЛР7 + ЛР9 + ЛР11 | Полная процессорная система RISC-V: тракт данных, LSU, прерывания |
| `lab-7/` | ЛР13 | Периферийные устройства: PS/2 + семисегментники, ПЛИС (ps2_hex) |
| `lab-8/` | ЛР14 | Высокоуровневое программирование: C → rv32i кросс-компиляция |

---

## lab-6 — Процессорная система RISC-V (ЛР7 + ЛР9 + ЛР11)

Три последовательных этапа построения одноциклового RISC-V процессора:

- **ЛР7** — `processor_core` (тракт данных): ALU, RegFile, Decoder, PC, 5 типов констант (I/U/S/B/J)
- **ЛР9** — `lsu` (Load-Store Unit): byte-enable для sw/sh/sb, знаковое/нулевое расширение для lb/lbu/lh/lhu, 1-тактовый stall для Block RAM
- **ЛР11** — `csr_controller` + `interrupt_controller` (mtvec/mepc/mstatus/mie/mscratch, irq_pending latch)

Базовые модули (`processor_core`, `lsu`, `alu`, `decoder` и др.) — переиспользуются в lab-7 и lab-8.

```bash
cd lab-6
iverilog -g2012 -o sim alu_opcodes_pkg.sv csr_pkg.sv decoder_pkg.sv memory_pkg.sv \
  fulladder.sv alu.sv decoder.sv register_file.sv \
  interrupt_subsystem.sv lsu.sv instr_mem.sv data_mem.sv \
  processor_core.sv processor_system.sv \
  lab_11.tb_processor_system.sv && vvp sim
```

Подробности — в [lab-6/README.md](lab-6/README.md), оригинальные задания — в [lab-6/TASK.md](lab-6/TASK.md).

---

## lab-7 — Периферийные устройства (ЛР13), вариант ps2_hex

Интеграция контроллеров PS/2 и семисегментных индикаторов в процессорную систему для прошивки на **Nexys A7-100T**.

- `sys_clk_rst_gen` — делитель частоты 100 МГц → 10 МГц
- `ps2_sb_ctrl` + `PS2Receiver` + `debouncer` — приём скан-кодов с прерыванием
- `hex_sb_ctrl` + `hex_digits` — вывод на 8 семисегментных индикаторов
- Шинный декодер: `addr[31:24]` → выбор устройства (0x00=dmem, 0x03=PS/2, 0x04=HEX)

SV-ядро берётся из `../lab-6/`. Для синтеза нужен Vivado — 20 `.sv` файлов + `program.mem` + `nexys_a7_100t.xdc`.

Подробности — в [lab-7/README.md](lab-7/README.md), оригинальное задание — в [lab-7/TASK.md](lab-7/TASK.md).

---

## lab-8 — Высокоуровневое программирование (ЛР14), вариант ps2_hex

Программа на C, компилируется кросс-компилятором `riscv32-none-elf-gcc` и запускается на процессоре из lab-6. По прерыванию от PS/2 выводит скан-код на два семисегментных индикатора.

```bash
cd lab-8
make all   # C → init_instr.mem + init_data.mem + disasm.S
make sim   # iverilog симуляция (3/3 тестов)
make wave  # GTKWave
```

Зависит от `../lab-6/` (SV-ядро). Кросс-компилятор доступен через `direnv allow` в корне репо.

Подробности — в [lab-8/README.md](lab-8/README.md), оригинальное задание — в [lab-8/TASK.md](lab-8/TASK.md).

---

## Инструменты

| Инструмент | Применение |
|---|---|
| `iverilog` + `vvp` | Симуляция (lab-1 .. lab-8) |
| `gtkwave` | Просмотр VCD-диаграмм |
| `verilator` | Альтернативная симуляция (lab-5+, с `import pkg::*`) |
| Vivado | Синтез, имплементация, прошивка ПЛИС (lab-6, lab-7) |
| `riscv32-none-elf-gcc` | Кросс-компиляция C для rv32i (lab-8) |

В каждой лабе есть `README.md` (практика) и, где применимо, `THEORY.md` (теория/синтаксис).