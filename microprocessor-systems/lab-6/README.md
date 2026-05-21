# Лабораторная работа №6 — Процессорная система RISC-V (ЛР7 + ЛР9 + ЛР11)

> **Оригинальные задания** — см. [TASK.md](TASK.md).  
> Исходники взяты из официального репозитория курса APS (МИЭТ):  
> - ЛР7 (Тракт данных): https://github.com/MPSU/APS/tree/master/Labs/07.%20Datapath  
> - ЛР9 (Интеграция LSU): https://github.com/MPSU/APS/tree/master/Labs/09.%20LSU%20Integration  
> - ЛР11 (Интеграция прерываний): https://github.com/MPSU/APS/tree/master/Labs/11.%20Interrupt%20integration

---

## Что реализовано

Данная лаба объединяет три последовательных этапа из курса APS:

| Этап | Что добавляется |
|---|---|
| **ЛР7** | `processor_core` (тракт данных) + `processor_system` с памятями |
| **ЛР9** | `lsu` (Load-Store Unit) интегрируется в `processor_system` вместо голого stall-регистра |
| **ЛР11** | `csr_controller` + `interrupt_controller` интегрируются внутрь `processor_core` |

---

## Архитектура системы

```
                         processor_system
   clk_i ──────────────────────────────────────────────────────────────────────┐
   rst_i ──────────────────────────────────────────────────────────────────────┤
                                                                                │
   ┌──────────────────────────────────────────────────────────────────────┐    │
   │  processor_core (core)                                               │    │
   │                                                                      │    │
   │  ┌──────────┐  a_sel/b_sel  ┌─────────────────┐                    │    │
   │  │ decoder  │──────────────►│       ALU        │                    │    │
   │  │          │  alu_op       │  (alu.sv +       │                    │    │
   │  │          │──────────────►│   fulladder.sv)  │                    │    │
   │  └──────────┘               └─────────────────┘                    │    │
   │       │ gpr_we, wb_sel           │ alu_result                       │    │
   │       ▼                          ▼                                  │    │
   │  ┌──────────────────┐   ┌────────────────────┐                     │    │
   │  │  register_file   │   │    PC register     │◄── stall_i          │    │
   │  │  x0–x31 (32×32b) │   │  (next_pc logic)   │                    │    │
   │  └──────────────────┘   └────────────────────┘                    │    │
   │                                  │ instr_addr_o                    │    │
   │  ┌──────────────────────────┐    │                                  │    │
   │  │  csr_controller          │    │ Константы I/U/S/B/J/Z           │    │
   │  │  mtvec, mepc, mstatus,   │    │ (знакорасширение из инструкции) │    │
   │  │  mie, mscratch           │    │                                  │    │
   │  └──────────────────────────┘    │                                  │    │
   │  ┌──────────────────────────┐    │                                  │    │
   │  │  interrupt_controller    │◄── irq_req (internal wire)           │    │
   │  │  trap, irq_pending latch │──► irq_ret (internal wire)           │    │
   │  └──────────────────────────┘                                      │    │
   │                                                                      │    │
   │  instr_i ◄──────────────────────────────────────────────────────   │    │
   │  mem_rd_i ◄─────────────────────────────────────────────────────   │    │
   │  mem_addr_o, mem_size_o, mem_req_o, mem_we_o, mem_wd_o ──────────► │    │
   └──────────────────────────────────────────────────────────────────────┘    │
                │                              │                                │
                │ instr_addr_o                 │ core_mem_* сигналы             │
                ▼                              ▼                                │
   ┌──────────────────┐         ┌─────────────────────────┐                   │
   │  instr_mem       │         │  lsu (lsu_unit)          │                   │
   │  (комбин., ROM)  │         │                          │◄── core_stall     │
   │  program.mem     │         │  sign ext / zero ext     │──► (stall_o)      │
   │  addr_i ──────── │         │  byte-enable генерация   │                   │
   │  read_data_o ◄─  │         │  1-такт stall при req    │                   │
   └──────────────────┘         └─────────────────────────┘                   │
                                              │ ext_mem_* сигналы              │
                                              ▼                                │
                                 ┌──────────────────────────┐                  │
                                 │  data_mem                │                  │
                                 │  (синхронная, BRAM)      │                  │
                                 │  addr_i, we_i, be_i      │                  │
                                 │  wd_i, rd_o              │                  │
                                 └──────────────────────────┘                  │
   └──────────────────────────────────────────────────────────────────────────┘
```

### Иерархия сигналов

| Сигнал | Откуда | Куда | Описание |
|---|---|---|---|
| `instr_addr` | `core.instr_addr_o` | `imem.addr_i` | PC — адрес инструкции |
| `instr` | `imem.read_data_o` | `core.instr_i` | 32-битная инструкция |
| `core_mem_addr/size/req/we/wd` | `core.*_o` | `lsu.*_i` | Запрос ядра к памяти |
| `core_mem_rd` | `lsu.rd_o` | `core.mem_rd_i` | Данные из памяти для ядра |
| `core_stall` | `lsu.stall_o` | `core.stall_i` | Заморозка PC на 1 такт |
| `ext_mem_addr/wd/we/be` | `lsu.mem_*_o` | `dmem.*_i` | Запрос LSU к data_mem |
| `ext_mem_rd` | `dmem.rd_o` | `lsu.mem_rd_i` | Данные из data_mem |
| `irq_req` | (тестбенч через `DUT.irq_req`) | `core.irq_req_i` | Запрос прерывания |
| `irq_ret` | `core.irq_ret_o` | (тестбенч через `DUT.irq_ret`) | Возврат из обработчика |

---

## Ключевые особенности реализации

### LSU — Логика stall и байтовые операции

LSU является посредником между ядром (32-битные операции) и data_mem (побайтовая запись).

**Stall при обращении к памяти:**
- При любом `req_i = 1` → LSU выставляет `stall_o = 1` на текущем такте
- `data_mem` — синхронная (Block RAM): данные появляются на выходе на следующем такте
- Ядро с `stall_i = 1` не продвигает PC и переисполняет текущую инструкцию
- На следующем такте `stall_o` падает в 0, данные уже стабильны на `rd_o`

**Byte Enable для Store:**

| Инструкция | `be_o` | Что пишется |
|---|---|---|
| `sw` | `4'b1111` | все 4 байта |
| `sh` (выровнено) | `4'b0011` | байты 0–1 |
| `sb` (байт 0) | `4'b0001` | только байт 0 |

**Sign Extension для Load:**

| Инструкция | Расширение | Результат |
|---|---|---|
| `lw` | нет | 32 бита |
| `lh` | знаковое | 16 бит + sign |
| `lhu` | нулями | 16 бит + 0 |
| `lb` | знаковое | 8 бит + sign |
| `lbu` | нулями | 8 бит + 0 |

### CSR Controller — системные регистры

| Регистр CSR | Адрес | Назначение |
|---|---|---|
| `mstatus` | `0x300` | глобальный флаг разрешения прерываний (бит MIE) |
| `mie` | `0x304` | маска источников прерываний |
| `mtvec` | `0x305` | адрес обработчика прерывания |
| `mscratch` | `0x340` | регистр для временного хранения |
| `mepc` | `0x341` | адрес возврата после `mret` |
| `mcause` | `0x342` | причина прерывания (`0x80000007`) |

### interrupt_controller — irq_pending latch

В данной реализации добавлен latch `irq_pending` для защиты от повторного trap пока выполняется обработчик:

```
irq_pending = 0 → при rst
irq_pending = 1 → при trap (вошли в обработчик)
irq_pending = 0 → при mret (вышли из обработчика)

trap = irq_req && (mstatus_mie || |mie_reg) && !irq_pending && !mret
```

Условие `|mie_reg` (вместо конкретного бита) нужно потому, что `program_11.mem` устанавливает `mie = 0x10000`, а не `mie = 0x1`.

---

## Файлы прошивок

| Файл | Для какого тестбенча | Содержимое |
|---|---|---|
| `program_07.mem` | `lab_07.tb_processor_system` | Листинг 1 ЛР7 (27 инструкций, все типы без CSR) |
| `program_11.mem` | `lab_11.tb_processor_system` | Программа ЛР10 (41 инструкция, с CSR и mret) |
| `program.mem` | активный файл (= `program_11.mem`) | используется при сборке |

> В Vivado `instr_mem.sv` загружает именно `program.mem` через `$readmemh`. При переключении между тестбенчами нужно копировать нужный файл в `program.mem` или подставлять нужное содержимое через Simulation Sources.

---

## Запуск в Vivado

### Шаг 1. Создать проект

**File → New Project** → RTL Project → Part: `xc7a100tcsg324-1` (Nexys A7-100T) или любой другой для симуляции.

### Шаг 2. Добавить Design Sources

Добавить все `.sv` файлы из `lab-6/`:

```
alu_opcodes_pkg.sv
csr_pkg.sv
decoder_pkg.sv
memory_pkg.sv
alu.sv
fulladder.sv
decoder.sv
register_file.sv
interrupt_subsystem.sv
lsu.sv
instr_mem.sv
data_mem.sv
processor_core.sv
processor_system.sv
```

Top module = `processor_system`.

### Шаг 3. Добавить Simulation Sources

Добавить **один** тестбенч и файл прошивки:

**Для проверки ЛР7 / ЛР9:**
- `lab_07.tb_processor_system.sv` → установить как Simulation Top
- `program_07.mem` (добавить как data-файл; или вручную скопировать содержимое в `program.mem`)

**Для проверки ЛР11:**
- `lab_11.tb_processor_system.sv` → установить как Simulation Top
- `program.mem` (= `program_11.mem`, добавить как data-файл)

> Чтобы добавить `.mem` как data-файл в Vivado: **Add Sources → Add or create simulation sources** → выбрать `.mem` файл. Vivado скопирует его в директорию симуляции.

### Шаг 4. Run Simulation

**Flow Navigator → Simulation → Run Behavioral Simulation**

Симуляция не выводит PASS/FAIL — проверка ручная по временной диаграмме (см. ниже).

---

## Что смотреть на временной диаграмме

### Тестбенч ЛР7 (`lab_07_tb_processor_system`)

Добавить в Waveform:

| Сигнал | Путь в иерархии | Что проверять |
|---|---|---|
| `clk` | `clk` | тактовый сигнал |
| `PC` | `DUT.core.instr_addr_o` | счётчик программы |
| `instr` | `DUT.instr` | текущая инструкция |
| `stall` | `DUT.core_stall` | = 1 при load/store |
| `mem_req` | `DUT.core_mem_req` | запрос к памяти |
| `mem_we` | `DUT.core_mem_we` | = 1 при store |
| `ext_mem_be` | `DUT.ext_mem_be` | byte-enable маска |
| `ext_mem_addr` | `DUT.ext_mem_addr` | адрес в data_mem |

Ожидаемый порядок (первые инструкции):
- PC=`0x00`: `addi x1, x0, 0x75C` → x1=`0x75C`
- PC=`0x04`: `addi x2, x0, 0x8A7` → x2=`0x8A7` (знакорасширение: `0xFFFFF8A7`)
- PC=`0x08`: `add x3, x1, x2` → x3=`0x75C+0xFFFFF8A7=0x3`
- PC=`0x18`: `jal x15, 0x50` → PC прыгает на `0x68`

### Тестбенч ЛР11 (`lab_11_tb_processor_system`)

Дополнительно смотреть:

| Сигнал | Путь | Что проверять |
|---|---|---|
| `irq_req` | `DUT.irq_req` | тестбенч устанавливает в 1 |
| `irq_ret` | `DUT.irq_ret` | = 1 при выполнении `mret` |
| `trap` | `DUT.core.*` | = 1 в такт прыжка на mtvec |
| `mtvec` | `DUT.core.*` | адрес обработчика (из CSR) |
| `mepc` | `DUT.core.*` | адрес возврата (сохранённый PC) |

Ожидаемый сценарий:
1. Тестбенч: `DUT.irq_req = 1` (один такт)
2. Следующий такт: PC прыгает на адрес из `mtvec`
3. Обработчик выполняет работу
4. Инструкция `mret` (код `0x30200073`): PC возвращается к `mepc`, `DUT.irq_ret = 1`

---

## Запуск через iverilog (локально)

```bash
# Проверка ЛР11 (program.mem уже = program_11.mem)
cd microprocessor-systems/lab-6
iverilog -g2012 -o sim \
  alu_opcodes_pkg.sv csr_pkg.sv decoder_pkg.sv memory_pkg.sv \
  fulladder.sv alu.sv decoder.sv register_file.sv \
  interrupt_subsystem.sv lsu.sv instr_mem.sv data_mem.sv \
  processor_core.sv processor_system.sv \
  lab_11.tb_processor_system.sv \
  && vvp sim

# Открыть диаграмму
gtkwave wave.vcd
```

```bash
# Проверка ЛР7 (нужна program_07.mem как program.mem)
cp program_07.mem program.mem
iverilog -g2012 -o sim \
  alu_opcodes_pkg.sv csr_pkg.sv decoder_pkg.sv memory_pkg.sv \
  fulladder.sv alu.sv decoder.sv register_file.sv \
  interrupt_subsystem.sv lsu.sv instr_mem.sv data_mem.sv \
  processor_core.sv processor_system.sv \
  lab_07.tb_processor_system.sv \
  && vvp sim
```

> Артефакты сборки (`sim`, `wave.vcd`, `obj_dir/`) не трекаются в git.
