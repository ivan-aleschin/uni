# Лабораторная работа №4 — Процессор CYBERcobra + индивидуальное задание

> **Оригинальная методичка** — см. [TASK.md](TASK.md).
> **Теория к защите** — см. [THEORY.md](THEORY.md).
> Источник: https://github.com/MPSU/APS/tree/master/Labs/04.%20Primitive%20programmable%20device

---

## Что реализовано

В лабе **две части**:

1. **CYBERcobra 3000 Pro 2.1** — простейший учебный процессор с архитектурой из методички. 5 типов инструкций, общая 32-битная кодировка. Реализован в `design.sv`.
2. **Индивидуальное задание (вариант 1)** — программа в машинных кодах, вычисляющая **циклический сдвиг вправо** `a ROR sw_i` для зашитой константы `a = 11`. Программа находится в `program.txt` (исходник) и `program.mem` (готовая для прошивки).

---

## Архитектура CYBERcobra

```
                                                       ┌──── +4 ────┐
                              ┌────────┐               │             │
              ┌── pc_q ──────►│        │ pc_addend     ▼             │
              │               │ MUX    │◄────── 32'd4 ──── 0         │
              │               │  PC    │◄── sext(off)<<2 ── 1        │
              │               └────┬───┘    take_branch_or_jump      │
              │                    │                                  │
              │                    ▼ pc_sum                           │
              │             ┌──────────┐                              │
              │             │fulladder │                              │
              │             │  32-bit  │                              │
              │             └────┬─────┘                              │
              │                  │                                    │
              │                  ▼ posedge clk_i                      │
              │            ┌─ PC_reg ─┐ ◄─ rst_i (0)                  │
              │            └───┬──────┘                                │
              └────────────────┘                                       │
                               │                                       │
                               ▼ pc_q                                  │
                       ┌───────────────┐                               │
                       │  instr_mem    │                               │
                       │   (asynch)    │                               │
                       └───────┬───────┘                               │
                               │ instr[31:0]                           │
                               │                                       │
                ┌──────────────┴───────────────┬──────────────────────┘
                │                              │
       ┌────────▼──────┐               ┌───────▼─────────┐
       │  decode       │               │ rf_const_sext   │
       │  J, B, WS,    │──┐            │ (23→32 знакрасш)│──► MUX rf_wd
       │  alu_op,      │  │            │ {16'b0, sw_i}   │──►   (WS)
       │  RA1/RA2/WA,  │  │            │ alu_result      │──►
       │  offset       │  │            └─────────────────┘
       └───────────────┘  │                  │
              │           │                  │ rf_wd
              ▼           ▼                  ▼
       ┌──────────────────────────────────────────┐
       │           register_file (32×32)          │
       │  RA1 → rf_rd1                             │
       │  RA2 → rf_rd2                             │
       │  WA, WE, WD ─ синхр. запись               │
       └──────────────────────────────────────────┘
              │ rf_rd1, rf_rd2          │ rf_rd1
              ▼                          ▼
       ┌─────────────┐              out_o
       │     ALU     │
       │  alu_op_i   │── alu_result ──►
       │  → flag_o   │── flag ─────────► take_branch_or_jump = J | (B & flag)
       └─────────────┘
```

Поля 32-битной инструкции:

```
 31    30    29:28    27:23     22:18     17:13     12:5         4:0
[J]   [B]   [WS]    [alu_op]   [RA1]     [RA2]    [const/off]   [WA]

WS=00 → const ← instr[27:5] (23 бита, sign-extended) → запись в RF
WS=01 → alu_result → запись в RF
WS=10 → {16'b0, sw_i} → запись в RF
```

---

## Индивидуальное задание (вариант 1, Алешин)

**Задача:** `out_o = a ROR sw_i` (циклический сдвиг вправо).

**Алгоритм:**
```
k = sw_i & 31                  // нормировка сдвига
result = (a >> k) | (a << (32-k))
```

В программе зашита константа `a = 11 = 0x0000000B`. Регистры:

| Регистр | Что хранит |
|---|---|
| r1 | a = 11 |
| r2 | sw_i |
| r3 | 31 (маска) |
| r4 | k = sw_i & 31 |
| r5 | 32 |
| r6 | 32 - k |
| r7 | a >> k |
| r8 | a << (32-k) |
| r9 | результат = r7 \| r8 |

Программа в человекочитаемом виде — `program.txt`, скомпилированная для памяти — `program.mem`.

**Ожидаемые результаты** (a = 11):

| sw_i (k) | out_o    |  Объяснение |
|---|---|---|
|  0 | `0x0000000B` | без сдвига |
|  1 | `0x80000005` | бит [0]=1 уехал в [31] |
|  2 | `0xC0000002` | биты [1:0]=11 уехали в [31:30] |
|  4 | `0xB0000000` | `1011` уехало в верхние 4 бита |
|  8 | `0x0B000000` | байт `0x0B` сдвинулся в верхнюю позицию |
| 16 | `0x000B0000` | полуслово |
| 31 | `0x00000016` | rotate на 31 ≡ rotate left на 1 |

---

## Файлы

| Файл | Назначение |
|---|---|
| `design.sv` | модули `CYBERcobra`, `instr_mem`, `register_file` |
| `lab1_adders.sv` | `fulladder32` из ЛР1 |
| `lab2_alu.sv` | `alu` из ЛР2 |
| `alu_opcodes_pkg.sv` | константы кодов АЛУ |
| `memory_pkg.sv` | константы размеров памяти |
| `program.txt` | программа индивидуального задания в псевдо-ассемблере |
| `program.mem` | она же после `cyberconverter` (готова для `$readmemh`) |
| `cyberconverter.cpp` | компилятор `program.txt → program.mem` |
| `lab_04.tb_cybercobra.sv` | официальный тестбенч (минимальный, без проверки) |
| `testbench.sv` | мой тестбенч с фиксированным `sw_i = 2` для отладки |
| `check_rotate.sv` | самопроверяющий тестбенч (7 значений k, эталон через ror32) |

---

## Запуск

### Самопроверка индивидуального задания (рекомендую первым)

```bash
cd microprocessor-systems/lab-4
iverilog -g2012 -o sim_check \
  memory_pkg.sv alu_opcodes_pkg.sv lab1_adders.sv lab2_alu.sv \
  design.sv check_rotate.sv \
  && vvp sim_check
```

Ожидаемый вывод:
```
OK   k=0  out=0000000b
OK   k=1  out=80000005
OK   k=2  out=c0000002
OK   k=4  out=b0000000
OK   k=8  out=0b000000
OK   k=16  out=000b0000
OK   k=31  out=00000016
[PASS] rotate-right test (variant 1): all cases OK
```

### Vivado (для сдачи)

1. Создать RTL-проект (`xc7a100tcsg324-1`).
2. **Design Sources**: `memory_pkg.sv`, `alu_opcodes_pkg.sv`, `lab1_adders.sv`, `lab2_alu.sv`, `design.sv`.
3. **Simulation Sources**: `lab_04.tb_cybercobra.sv`.
4. Добавить `program.mem` как **data file** (Add or create simulation sources → Data file).
5. Top module = `CYBERcobra`. Simulation top = `tb_cybercobra`.
6. **Run Behavioral Simulation**.

В тестбенче `lab_04.tb_cybercobra.sv` нет автоматических проверок — нужно вручную смотреть waveform. Полезные сигналы:

| Сигнал | Что смотреть |
|---|---|
| `DUT.pc_q` | программный счётчик |
| `DUT.instr` | текущая инструкция |
| `DUT.rf.rf_mem[1..9]` | состояния регистров r1..r9 |
| `DUT.alu_result` | результат текущей АЛУ-операции |
| `out_o` | финальный результат |

### Перекомпиляция программы (если правишь `program.txt`)

```bash
cd microprocessor-systems/lab-4
g++ -o cyberconverter cyberconverter.cpp
./cyberconverter program.txt program.mem
```

### Проверка в ПЛИС (Nexys A7)

Папка `board files/` оригинального репозитория содержит wrapper, подключающий `CYBERcobra` к переключателям и светодиодам. В моей сдаче я этот wrapper не дублировал — его можно скопировать из репо MPSU при подготовке к защите в железе.

---

## Теория для защиты

См. [THEORY.md](THEORY.md): принцип работы PC, мультиплексирование источников записи, знакорасширение константы, особенности АЛУ (срез `[4:0]` для сдвигов).
