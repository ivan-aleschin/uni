# Лабораторная работа №8 — Высокоуровневое программирование (ЛР14)

> **Оригинальное задание** — см. [TASK.md](TASK.md).  
> Исходники взяты из официального репозитория курса APS (МИЭТ):  
> https://github.com/MPSU/APS/tree/master/Labs/14.%20Programming

**Вариант:** Алешин Иван Кириллович → Клавиатура PS/2 → Семисегментники (`ps2_hex`)

---

## Что реализовано

Программа на языке C компилируется кросс-компилятором `riscv32-none-elf-gcc` и запускается на процессоре RISC-V из lab-6. При каждом прерывании от PS/2 клавиатуры обработчик считывает скан-код и выводит его на два семисегментных индикатора.

---

## Архитектура системы

```
   Тестбенч
   ─────────────────────────────────────────────────────────────
   clk ──────────────────────────────────────────────────────────┐
   rst ──────────────────────────────────────────────────────────┤
   irq_req_i ────► (1-тактовый импульс при новом скан-коде) ────►┤
   ps2_i ──────────────────────────────────────────────────────►│
                                                                  │
                    lab-8 processor_system                        │
   ┌──────────────────────────────────────────────────────────┐  │
   │                                                          │  │
   │  ┌─────────────────────────────────────────────────┐    │  │
   │  │  processor_core  (из lab-6)                     │    │  │
   │  │  ALU + RegFile + Decoder                        │    │  │
   │  │  csr_controller (mtvec, mepc, mstatus, mie)     │    │  │
   │  │  interrupt_controller (irq_pending latch)       │    │  │
   │  └─────────────────────────────────────────────────┘    │  │
   │                │ mem_req/addr/we/wd/size                 │  │
   │                ▼                                         │  │
   │  ┌──────────────────┐                                    │  │
   │  │      LSU          │  (из lab-6)                      │  │
   │  │  sign/zero-ext    │  stall_o ──► core.stall_i        │  │
   │  │  byte-enable      │                                   │  │
   │  └──────────────────┘                                    │  │
   │          │ ext_mem_addr[31:24]                           │  │
   │          │                                               │  │
   │   ┌──────┼──────────────┬──────────────────┐            │  │
   │   │0x00  │ 0x03         │                  │ 0x04        │  │
   │   ▼      ▼              │                  ▼            │  │
   │ data_mem  rd=ps2_i      │           HEX регистры        │  │
   │ (2 KiB)   (write ignd)  │           hex0_o ─────────────┼─►│
   │ init_data                           hex1_o ─────────────┼─►│
   │                                     addr[4:2]=0/1       │  │
   │  instr_mem (1 KiB) ◄── init_instr.mem (.text)           │  │
   └──────────────────────────────────────────────────────────┘  │
   irq_ret_o ◄───────────────────────────────────────────────────┤
   hex0_o ──────────────────────────────────────────────────────►│
   hex1_o ──────────────────────────────────────────────────────►│
   ─────────────────────────────────────────────────────────────
```

### Карта адресов (симуляция)

| Адрес | Поле в `platform.h` | Операция | Описание |
|---|---|---|---|
| `0x03000000` | `ps2_ptr->scan_code` | R | Возвращает `ps2_i` (из тестбенча) |
| `0x03000024` | `ps2_ptr->rst` | W | Игнорируется в симуляции |
| `0x04000000` | `hex_ptr->hex0` | W | → порт `hex0_o` |
| `0x04000004` | `hex_ptr->hex1` | W | → порт `hex1_o` |

---

## Структура файлов

| Файл | Источник | Описание |
|---|---|---|
| `main.c` | свой | C-программа: `main()` + `int_handler()` |
| `platform.h` | APS | Указатели на структуры периферии |
| `startup.S` | APS | Инициализация BSS, стека, CSR, `_int_handler` |
| `linker_script.ld` | APS | instr_mem 1 КБ, data_mem 2 КБ |
| `memory_pkg.sv` | свой | INSTR=1024Б, DATA=2048Б |
| `instr_mem.sv` | свой | ПЗУ инструкций → `init_instr.mem` |
| `data_mem.sv` | свой | ОЗУ данных → `init_data.mem` |
| `processor_system.sv` | свой | Декодер шины + HEX регистры + mux PS/2 |
| `lab_14.tb_processor_system.sv` | свой | Тестбенч: 3 скан-кода (0x1C, 0x32, 0xAB) |
| `Makefile` | свой | `make all` → .mem, `make sim` → iverilog |
| `init_instr.mem` | generated | Скомпилированный `.text` раздел |
| `init_data.mem` | generated | Скомпилированный `.data` раздел (пустой) |
| `disasm.S` | generated | Дизассемблер для отладки по PC |

SV-ядро (`processor_core`, `lsu`, `alu`, `decoder` и др.) **не дублируется** — `Makefile` ссылается на `../lab-6/`.

---

## Программа (`main.c`)

```c
#include "platform.h"
#include <stdint.h>

void int_handler(void)
{
    uint32_t code = ps2_ptr->scan_code;   // читаем из 0x03000000
    hex_ptr->hex0 = code & 0xFu;          // пишем в 0x04000000
    hex_ptr->hex1 = (code >> 4) & 0xFu;  // пишем в 0x04000004
    ps2_ptr->rst = 1u;                    // сброс PS/2 (0x03000024, игнор)
}

int main(void) { while (1) { } return 0; }
```

**Поток выполнения:**
1. `startup.S` инициализирует `sp`/`gp`/`mtvec`/`mie`, вызывает `main`
2. `main` — бесконечный цикл ожидания прерывания
3. `irq_req_i = 1` → ядро прыгает на `_int_handler` (asm в startup.S)
4. `_int_handler` сохраняет контекст, вызывает `int_handler` (C-функцию), восстанавливает, `mret`

---

## Сборка и запуск

```bash
cd microprocessor-systems/lab-8

make all     # C → init_instr.mem + init_data.mem + disasm.S
make sim     # iverilog симуляция (vvp)
make wave    # открыть GTKWave
make clean   # удалить артефакты (.o, .elf, .mem, sim)
```

Кросс-компилятор `riscv32-none-elf-gcc` доступен через direnv (`direnv allow` в корне репо).

### Ручные шаги

```bash
riscv32-none-elf-gcc -c -march=rv32i_zicsr -mabi=ilp32 startup.S -o startup.o
riscv32-none-elf-gcc -c -march=rv32i_zicsr -mabi=ilp32 -O2 -ffreestanding -nostdlib main.c -o main.o
riscv32-none-elf-gcc -march=rv32i_zicsr -mabi=ilp32 -Wl,--gc-sections -nostartfiles \
  -T linker_script.ld startup.o main.o -o result.elf

riscv32-none-elf-objcopy -O verilog --verilog-data-width=4 -j .text result.elf init_instr.mem
riscv32-none-elf-objcopy -O verilog --verilog-data-width=4 \
  -j .data -j .bss -j .sdata result.elf init_data.mem
sed -i '/^@/d' init_data.mem    # удалить LMA-строку @20000000

riscv32-none-elf-objdump -D result.elf > disasm.S
```

> `--verilog-data-width=4` — экспорт по 4 байта в ячейку (для 32-битного `$readmemh`).  
> `sed -i '/^@/d'` — секция `.data` имеет LMA=`0x00800000`, строка `@20000000` нарушает инициализацию.

---

## Запуск в Vivado

### Design Sources

Из `../lab-6/`:
```
alu_opcodes_pkg.sv  csr_pkg.sv  decoder_pkg.sv
fulladder.sv  alu.sv  decoder.sv  register_file.sv
interrupt_subsystem.sv  lsu.sv  processor_core.sv
```

Из `lab-8/`:
```
memory_pkg.sv  instr_mem.sv  data_mem.sv  processor_system.sv
```

Top = `processor_system`.

### Simulation Sources

```
lab_14.tb_processor_system.sv   ← Top Simulation
init_instr.mem                  ← data file
init_data.mem                   ← data file
```

> Добавление `.mem` как data-файла: **Add Sources → Add or create simulation sources**.

### Ожидаемый вывод (Tcl Console)

```
[PASS] ps2=0x1C → hex0=0xc hex1=0x1
[PASS] ps2=0x32 → hex0=0x2 hex1=0x3
[PASS] ps2=0xAB → hex0=0xb hex1=0xa
=== Итог: 3/3 тестов прошло ===
```

---

## Что смотреть на диаграмме

| Сигнал | Путь | Что проверять |
|---|---|---|
| `PC` | `DUT.core.instr_addr_o` | Адрес инструкции |
| `irq_req_i` | `irq_req_i` | Один такт = 1 |
| `irq_ret_o` | `irq_ret_o` | = 1 при `mret` |
| `ps2_i` | `ps2_i` | Скан-код |
| `hex0_o` | `hex0_o` | Младший ниббл |
| `hex1_o` | `hex1_o` | Старший ниббл |

По PC на диаграмме ориентируйтесь через `disasm.S`: найдите `_int_handler`, `int_handler`, `main`.

---

## Отличия от lab-6 и lab-7

| Параметр | lab-6 (ЛР7/9/11) | lab-7 (ЛР13) | lab-8 (ЛР14) |
|---|---|---|---|
| Цель | Верификация HW | HW + реальная периферия | Верификация SW |
| `processor_system` | внутр. `irq_req/ret` | HW периферия + `sys_clk_rst_gen` | внешние порты `irq_req_i/ret_o` |
| PS/2 | нет | `PS2Receiver` (реальный) | `ps2_i` — прямой вход |
| HEX | нет | `hex_digits` (реальный) | `hex0_o/hex1_o` — прямые выходы |
| INSTR_MEM | 512 Б | 512 Б | **1024 Б** |
| DATA_MEM | 512 Б | 512 Б | **2048 Б** |
| Тестбенч | ручная проверка | `peripheral_pkg` задачи | автоматическая PASS/FAIL |
