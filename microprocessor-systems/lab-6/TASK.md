# Оригинальные задания — ЛР7 + ЛР9 + ЛР11

> Источник: репозиторий APS (Architectures of Processor Systems), МИЭТ
>
> - ЛР7: https://github.com/MPSU/APS/tree/master/Labs/07.%20Datapath
> - ЛР9: https://github.com/MPSU/APS/tree/master/Labs/09.%20LSU%20Integration
> - ЛР11: https://github.com/MPSU/APS/tree/master/Labs/11.%20Interrupt%20integration

Данная лабораторная работа объединяет три последовательных этапа построения процессорной системы RISC-V.

---

## ЛР7 — «Тракт данных»

### Цель

Описать на языке SystemVerilog процессор с архитектурой RISC-V, реализовав его тракт данных и подключив устройство управления. Итогом станет процессор RISC-V, работающий с памятью данных посредством 32-битных слов (БЕЗ инструкций lh, lhu, lb, lbu, sh, sb).

### Прототип `processor_core` (ЛР7)

```systemverilog
module processor_core (
  input  logic        clk_i,
  input  logic        rst_i,
  input  logic        stall_i,
  input  logic [31:0] instr_i,
  input  logic [31:0] mem_rd_i,
  output logic [31:0] instr_addr_o,
  output logic [31:0] mem_addr_o,
  output logic [ 2:0] mem_size_o,
  output logic        mem_req_o,
  output logic        mem_we_o,
  output logic [31:0] mem_wd_o
);
endmodule
```

### Прототип `processor_system` (ЛР7)

```systemverilog
module processor_system(
  input  logic clk_i,
  input  logic rst_i
);
endmodule
```

Обратите внимание на **регистр stall** в ЛР7: поскольку используется блочная память ПЛИС с задержкой 1 такт, при обращении к памяти программный счётчик должен быть заморожен ровно на 1 такт. В ЛР7 эта логика описывалась прямо в `processor_system` через отдельный регистр (flip-flop). В ЛР9 эта логика перемещается внутрь модуля `lsu`.

### Задание ЛР7

1. Реализовать ядро процессора RISC-V по предложенной микроархитектуре (`processor_core`).
2. Подключить к нему память инструкций и память данных в модуле `processor_system`.
   - При создании экземпляра `processor_core` использовать имя сущности `core` (т.е. `processor_core core(...)`).
3. Проверить работу системы с помощью тестовой программы (файл `program_07.mem` / `lab_07.tb_processor_system.sv`).
4. Написать собственную программу на ассемблере RISC-V по индивидуальному заданию из ЛР4.
5. Проверить работоспособность на ПЛИС.

### Тестовая программа (Листинг 1, ЛР7)

```
00:  addi  x1,  x0, 0x75С       // 0x75C00093
04:  addi  x2,  x0, 0x8A7       // 0x8A700113
08:  add   x3,  x1, x2          // 0x002081B3
0C:  and   x4,  x1, x2          // 0x0020F233
10:  sub   x5,  x4, x3          // 0x403202B3
14:  mul   x6,  x3, x4          // 0x02418333  (неподдерживаемая инструкция)
18:  jal   x15, 0x50            // 0x050007EF  (прыжок на 0x68)
1C:  jalr  x15, 0x0(x6)         // 0x000307E7
20:  slli  x7,  x5, 31          // 0x01F29393
24:  srai  x8,  x7, 1           // 0x4013D413
28:  srli  x9,  x8, 29          // 0x01D45493
2C:  lui   x10, 0xfadec          // 0xFADEC537
30:  addi  x10, x10, -1346      // 0xABE50513
34:  sw    x10, 0x0(x4)         // 0x00A22023
38:  sh    x10, 0x6(x4)         // 0x00A21323
3C:  sb    x10, 0xb(x4)         // 0x00A205A3
40:  lw    x11, 0x0(x4)         // 0x00022583
44:  lh    x12, 0x0(x4)         // 0x00021603
48:  lb    x13, 0x0(x4)         // 0x00020683
4C:  lhu   x14, 0x0(x4)         // 0x00025703
50:  lbu   x15, 0x0(x4)         // 0x00024783
54:  auipc x16, 0x00004         // 0x00004817
58:  bne   x3,  x4, 0x08        // 0x00321463
5C:  (нулевая инструкция)        // 0x00000000
60:  jal   x17, 0x00004         // 0x004008EF
64:  jalr  x14, 0x0(x17)        // 0x00088767
68:  jalr  x18, 0x4(x15)        // 0x00478967
```

Файл с прошивкой для ЛР7: `program_07.mem`

---

## ЛР9 — «Интеграция блока загрузки и сохранения»

### Цель

Интегрировать модуль `lsu` в модуль `processor_system`, реализованный в ЛР7.

### Задание ЛР9

1. Интегрировать модули `lsu` и `data_mem` в модуль `processor_system`.
   - **Убрать** из `processor_system` логику сигнала `stall` — она переходит внутрь модуля `lsu`.
2. Проверить процессорную систему с помощью программы и тестбенча из ЛР7 (`lab_07.tb_processor_system.sv`, `program_07.mem`).
   - Обратить особое внимание на исполнение инструкций sw, sh, sb, lw, lh, lb, lhu, lbu.
3. Проверка в ПЛИС не предусмотрена.

---

## ЛР11 — «Интеграция подсистемы прерывания»

### Цель

Интегрировать модули `csr_controller` и `interrupt_controller` в модуль `processor_core`.

### Прототип `processor_core` (ЛР11, финальный)

```systemverilog
module processor_core (
  input  logic        clk_i,
  input  logic        rst_i,
  input  logic        stall_i,
  input  logic [31:0] instr_i,
  input  logic [31:0] mem_rd_i,
  input  logic        irq_req_i,     // новый вход
  output logic [31:0] instr_addr_o,
  output logic [31:0] mem_addr_o,
  output logic [ 2:0] mem_size_o,
  output logic        mem_req_o,
  output logic        mem_we_o,
  output logic [31:0] mem_wd_o,
  output logic        irq_ret_o      // новый выход
);
endmodule
```

### Правки `processor_system` для ЛР11

В модуле `processor_system` создать внутренние провода и подключить их к ядру:

```systemverilog
logic irq_req;   // другой конец — не подключён (используется тестбенчем через DUT.irq_req)
logic irq_ret;   // другой конец — не подключён (используется тестбенчем через DUT.irq_ret)
```

> **Важно:** Имена проводов должны быть именно `irq_req` и `irq_ret` — они используются верификационным окружением при иерархическом доступе (`DUT.irq_req`, `DUT.irq_ret`).

### Задание ЛР11

1. Заменить `program.mem` на файл для ЛР11 (`program_11.mem`).
2. Интегрировать `csr_controller` и `interrupt_controller` внутрь `processor_core`.
   - Добавить константу `imm_Z` (расширяется нулями, а не знаковым битом).
3. Обновить экземпляр `processor_core` в `processor_system` с учётом новых портов (`irq_req_i`, `irq_ret_o`).
4. Проверить модуль с помощью `lab_11.tb_processor_system.sv`.
5. Проверка в ПЛИС не предусмотрена.

### Тестовая программа (ЛР11)

Файл с прошивкой: `program_11.mem` (он же `program.mem`). Содержит программу из Листинга 1 ЛР10, которая инициализирует `mtvec`, включает прерывания через `mstatus`/`mie` и уходит в бесконечный цикл ожидания.

---

## Особенности реализации interrupt_controller

По сравнению с оригинальным шаблоном из ЛР10, в данной реализации добавлен `irq_pending` latch:

```systemverilog
logic irq_pending;
always_ff @(posedge clk_i) begin
    if (rst_i)        irq_pending <= 1'b0;
    else if (trap_o)  irq_pending <= 1'b1;
    else if (mret_i)  irq_pending <= 1'b0;
end
assign trap_o = irq_req_i && (mstatus_mie_i || |mie_reg_i) && !irq_pending && !mret_i;
```

Это предотвращает повторный trap пока обработчик не выполнит `mret`. Условие `|mie_reg_i` (вместо `mie_reg_i[7]`) нужно потому, что `program.mem` (program_11) устанавливает `mie=0x10000` (бит 16), а не бит 7.
