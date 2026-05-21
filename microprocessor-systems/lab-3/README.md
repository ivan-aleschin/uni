# Лабораторная работа №3 — Регистровый файл и память инструкций

> **Оригинальная методичка** — см. [TASK.md](TASK.md).
> Источник: https://github.com/MPSU/APS/tree/master/Labs/03.%20Register%20file%20and%20memory

---

## Что реализовано

Два независимых модуля памяти, которые далее переиспользуются во всех старших лабах (ЛР4, ЛР7, ЛР9, ЛР11, ЛР13, ЛР14):

| Модуль | Тип | Чтение | Запись | Размер |
|---|---|---|---|---|
| `instr_mem` | ROM | **асинхронное** | — (инициализация из `program.mem`) | 128 × 32 бит (= 512 байт) |
| `register_file` | 3-портовая RAM | 2 порта **асинхронных** | 1 порт **синхронный** | 32 × 32 бит |

---

## Архитектура

```
                                ┌───────────────────────────┐
                  read_addr_i ──►│                           │
                  (32 bit)       │  instr_mem  (ROM, async)  │──► read_data_o
                                 │  индекс = addr[8:2]       │   (32 bit)
                  program.mem ──►│  $readmemh инициализация  │
                                 └───────────────────────────┘

                              ┌─────────────────────────────────┐
                read_addr1_i ─►│                                  │──► read_data1_o
                read_addr2_i ─►│       register_file              │──► read_data2_o
                               │                                  │   (асинхронно)
                               │   ┌──────────────────────┐      │
                               │   │  rf_mem[0:31]        │      │
                               │   │   32 × 32 бит        │      │
                               │   └──────────────────────┘      │
                write_addr_i ─►│                                  │
                write_data_i ─►│   запись синхронно по posedge   │
              write_enable_i ─►│   clk_i; адрес 0 игнорируется   │
                       clk_i ─►│                                  │
                               └─────────────────────────────────┘
```

### Особенность: регистр `x0` = аппаратный 0

В RISC-V регистр `x0` всегда читается как 0 [Volume I: Unprivileged ISA, стр. 21]. В моей реализации это сделано **мультиплексором на выходах чтения**:

```systemverilog
assign read_data1_o = (read_addr1_i == 5'd0) ? 32'd0 : rf_mem[read_addr1_i];
assign read_data2_o = (read_addr2_i == 5'd0) ? 32'd0 : rf_mem[read_addr2_i];
```

И **дополнительно** запрещена запись в `rf_mem[0]`:

```systemverilog
if (write_enable_i && write_addr_i != 5'd0)
  rf_mem[write_addr_i] <= write_data_i;
```

Двойная защита: даже если по какой-то причине запись пройдёт, чтение всё равно вернёт 0.

### Особенность: побайтовая адресация в `instr_mem`

RISC-V обращается к памяти **по байтам** (каждой инструкции в 4 байта соответствует адрес, кратный 4: `0x00, 0x04, 0x08, …`), но реально `instr_mem` — это массив 32-битных слов с индексами `0, 1, 2, …`.

Поэтому два младших бита адреса отбрасываются:

```systemverilog
assign read_data_o = ROM[read_addr_i[$clog2(INSTR_MEM_SIZE_BYTES)-1:2]];
```

- `$clog2(512) = 9` → срез `[8:2]` → 7 бит → 128 ячеек, ровно `INSTR_MEM_SIZE_WORDS`.
- Старшие биты адреса (`[31:9]`) **игнорируются** — обращение по несуществующему адресу вернёт данные младших ячеек, без ошибки (так требует методичка).

---

## Файлы

| Файл | Назначение |
|---|---|
| `memory_pkg.sv` | константы `INSTR_MEM_SIZE_BYTES = 512`, `DATA_MEM_SIZE_BYTES = 512` |
| `design.sv` | мои `instr_mem` и `register_file` |
| `lab_03.tb_register_file.sv` | официальный тестбенч с reference-моделью |
| `testbench.sv` | мой минимальный smoke-test для локальной отладки |
| `program.mem` | (опционально) данные для инициализации `instr_mem` |

---

## Запуск тестбенча

### Vivado (рекомендуемый путь — это путь, который требует методичка)

1. **File → New Project** → RTL Project → Part `xc7a100tcsg324-1` (Nexys A7-100T).
2. **Add Sources → Add or create design sources** → добавить `memory_pkg.sv`, `design.sv`.
3. **Add Sources → Add or create simulation sources** → добавить `lab_03.tb_register_file.sv`.
4. **Set as Top** → `lab_03_tb_register_file` (в Simulation Sources).
5. **Flow Navigator → Run Simulation → Run Behavioral Simulation**.
6. В TCL Console должно появиться:
   ```
   Test has been started
   Test has been finished
   Number of errors:           0
   ```

### Локально через Verilator (для self-check)

```bash
cd microprocessor-systems/lab-3
verilator --binary --sv --timing \
  -Wno-INITIALDLY -Wno-WIDTH -Wno-UNOPTFLAT \
  -Wno-CASEINCOMPLETE -Wno-MULTIDRIVEN -Wno-CMPCONST -Wno-fatal \
  memory_pkg.sv design.sv lab_03.tb_register_file.sv \
  --top-module lab_03_tb_register_file -o sim_v
./obj_dir/sim_v
```

> ⚠ Под Verilator тест выдаёт **2 ложноположительные ошибки**:
> 1. *"The register file should not be initialized..."* — Verilator инициализирует память в `0` (а не `x`), поэтому проверка `32'hx !== RD1` срабатывает ложно.
> 2. *"invalid memory size"* — Verilator корректно ловит out-of-bounds (`rf_mem[32]`), но возвращает не `x`, а нули, и проверка тестбенча даёт ложный позитив.
>
> Это **ограничения Verilator**, а не моего кода. В Vivado/xsim обе проверки проходят корректно. Остальные ~32 проверки (сравнение с reference-моделью) идут без ошибок и в Verilator.

### Локально через iverilog — не работает

iverilog не поддерживает:
- `$timeformat` с 4 аргументами (используется в строке 66 тестбенча);
- `constant selects in always_*` (используется в `register_file_ref`, строки 220–249).

Поэтому iverilog для этой лабы не подходит. Используется Verilator (или Vivado).

---

## Проверка в ПЛИС

Методичка требует проверить регистровый файл на Nexys A7 через wrapper из папки `board files/` оригинального репозитория. В моём репо эта проверка не выделена в отдельный wrapper — `register_file` напрямую инстанцируется в CYBERcobra (ЛР4) и процессорном ядре (ЛР7+), и работает в железе уже там.

---

## Теория для защиты

См. [THEORY.md](THEORY.md):

- почему `x0` — аппаратный ноль;
- байтовая vs словесная адресация;
- асинхронное vs синхронное чтение и почему это важно;
- какой тип памяти ПЛИС использует под `rf_mem` и под `instr_mem` (распределённая vs блочная).
