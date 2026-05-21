# Лабораторная работа №7 — Процессорная система с периферией (ЛР13)

**Вариант:** Алешин Иван Кириллович → Клавиатура PS/2 → Семисегментники (`ps2_hex`)

> **Оригинальное задание** — см. [TASK.md](TASK.md).  
> Исходники лабораторной взяты из официального репозитория курса APS (МИЭТ):  
> https://github.com/MPSU/APS/tree/master/Labs/13.%20Peripheral%20units

---

## Архитектура системы

Система построена на основе однотактного RISC-V ядра и расширена контроллерами периферии.

```
           100 МГц                      10 МГц (sysclk)
clk_i ───► sys_clk_rst_gen ──────────────────────────────────┐
resetn_i ─► (делитель /10) ──► rst (active-high)             │
                                                              ▼
                                ┌──────────────────────────────────────────┐
                                │  processor_core (RISC-V rv32i)           │
                                │   ┌──────────┐ ┌─────┐ ┌──────────────┐ │
                                │   │ Register │ │ ALU │ │ CSR / IRQ    │ │
                                │   │ File     │ │     │ │ Controller   │ │
                                │   └──────────┘ └─────┘ └──────────────┘ │
                                └──────────────────────────────────────────┘
                                       │ mem_req/addr/wd/size
                                       ▼
                                ┌─────────────┐
                                │     LSU     │  byte-enable, stall
                                └─────────────┘
                                       │
               ┌───────────────────────┼──────────────────┐
               │ addr[31:24]=0x00      │ addr[31:24]=0x03  │ addr[31:24]=0x04
               ▼                       ▼                   ▼
          data_mem (512 Б)       ps2_sb_ctrl           hex_sb_ctrl
                                  ┌──────────┐         ┌──────────┐
                                  │PS2Receiver│        │hex_digits│
                                  │kclk/kdata │        │hex_led_o │
                                  └──────────┘         │hex_sel_o │
                                  irq_req_o ───►core   └──────────┘
```

### Карта адресов периферийной шины

| Адрес (верхний байт) | Устройство | Смещение | Регистр |
|---|---|---|---|
| `0x00xxxxxx` | data_mem (ОЗУ 512 Б) | — | — |
| `0x03000020` | PS/2 scan_code | +0x20 | read: принятый скан-код |
| `0x03000024` | PS/2 reset | +0x24 | write 1: сбросить флаг принятого байта |
| `0x04000000` | HEX hex0 | +0x00 | write: значение цифры 0 |
| `0x04000004` | HEX hex1 | +0x04 | write: значение цифры 1 |
| `0x04000020` | HEX bitmask | +0x20 | маска активных цифр (по умолчанию 0xFF) |

### Алгоритм работы (ps2_hex)

1. Прерывание PS/2 (`ps2_irq_req`) активируется, когда `PS2Receiver` принял новый байт.
2. Ядро прыгает на обработчик прерывания (адрес из `mtvec`).
3. Прошивка читает скан-код из `0x03000020`, записывает `hex0 = code & 0xF`, `hex1 = code >> 4`, затем сбрасывает PS/2 (`0x03000024 = 1`).
4. `mret` возвращает управление в `main`.
5. `hex_sb_ctrl` мультиплексирует восемь цифр на общие сегментные линии через `hex_digits`.

---

## Запуск в Vivado

### Шаг 1. Создать проект

1. **File → New Project** → Next → имя и директория → Next.
2. Выбрать **RTL Project**, снять галочку «Do not specify sources at this time» → Next.
3. Плата: **Nexys A7-100T** (или Part: `xc7a100tcsg324-1`).

### Шаг 2. Добавить Design Sources

**Project Manager → Add Sources → Add or create design sources**

Добавить все `.sv` файлы из директории `lab-7/` **кроме тестбенча**:

```
alu_opcodes_pkg.sv
csr_pkg.sv
decoder_pkg.sv
memory_pkg.sv
peripheral_pkg.sv
lab_02.alu.sv
lab_03.register_file.sv
lab_06.data_mem.sv
lab_08.lsu.sv
lab_10.csr.sv
lab_10.irq.sv
decoder.sv
hex_digits.sv
hex_sb_ctrl.sv
instr_mem.sv
PS2Receiver.sv
ps2_sb_ctrl.sv
processor_core.sv
processor_system.sv
sys_clk_rst_gen.sv
```

После добавления убедитесь, что Top module = `processor_system` (подсвечен жирным в иерархии).

### Шаг 3. Добавить Simulation Sources

**Project Manager → Add Sources → Add or create simulation sources**

Добавить два файла:
- `lab_13.tb_processor_system.sv`
- `program.mem` — **обязательно**, иначе `$readmemh` не найдёт прошивку

После добавления: в иерархии Simulation Sources выбрать `lab_13_tb_processor_system` как Top (правая кнопка → Set as Top).

### Шаг 4. Добавить Constraints

**Project Manager → Add Sources → Add or create constraints**

Добавить `nexys_a7_100t.xdc`.

### Шаг 5. Запустить симуляцию

**Flow Navigator → Simulation → Run Behavioral Simulation**

В окне Tcl Console появится вывод тестбенча. Тестбенч отправляет три PS/2 скан-кода (`0x1C`, `0xF0 1C`, `0x32`, `0xF0 32`, `0x21`, `0xF0 21`), пары make/break. Время симуляции — 4 мс (`#4ms $finish`).

#### Что смотреть на диаграмме

Добавить в Waveform следующие сигналы:

| Сигнал | Путь | Что видеть |
|---|---|---|
| `sysclk` | `DUT.sysclk` | 10 МГц (период 100 нс) |
| `irq_req` | `DUT.irq_req` | Импульс = PS/2 принял байт |
| `irq_ret` | `DUT.irq_ret` | Импульс = `mret` в обработчике |
| `hex_led_o` | `DUT.hex_led_o` | 7-сегментный код активной цифры |
| `hex_sel_o` | `DUT.hex_sel_o` | Мультиплексирование цифр |
| `ps2_clk` | `ps2_clk` | PS/2 тактовая (из тестбенча) |
| `ps2_dat` | `ps2_dat` | PS/2 данные (из тестбенча) |
| `stall_sig` | `DUT.stall_sig` | Stall при обращении к памяти |

Готовый файл конфигурации волн — `lab_13_tb_processor_system_behav.wcfg` — можно открыть через **File → Open Waveform Configuration** в окне симулятора.

### Локальная симуляция через Verilator (smoke-test)

В Vivado есть встроенная библиотека `unisim` с примитивом `BUFG` (clock buffer), которым пользуется `sys_clk_rst_gen`. Для Verilator нужна заглушка — она лежит в `bufg_stub.sv` (этот файл **не нужно добавлять в Vivado-проект**).

```bash
cd microprocessor-systems/lab-7
verilator --binary --sv --timing \
  -Wno-fatal -Wno-WIDTH -Wno-UNUSED -Wno-UNDRIVEN -Wno-MULTIDRIVEN -Wno-MULTITOP \
  --top-module lab_13_tb_processor_system \
  bufg_stub.sv \
  memory_pkg.sv alu_opcodes_pkg.sv decoder_pkg.sv csr_pkg.sv peripheral_pkg.sv \
  lab_03.register_file.sv lab_02.alu.sv decoder.sv instr_mem.sv \
  lab_06.data_mem.sv lab_08.lsu.sv lab_10.csr.sv lab_10.irq.sv \
  sys_clk_rst_gen.sv hex_digits.sv hex_sb_ctrl.sv \
  PS2Receiver.sv ps2_sb_ctrl.sv \
  processor_core.sv processor_system.sv lab_13.tb_processor_system.sv \
  -o sim_lr13 \
  && ./obj_dir/sim_lr13
```

Симуляция длится 4 мс (`#4ms $finish` в тестбенче). Тестбенч пассивный — нет PASS/FAIL, поэтому смотрите waveform отдельно.

### Шаг 6. Синтез и прошивка платы (опционально)

1. **Run Synthesis** → **Run Implementation** → **Generate Bitstream**.
2. Подключить плату Nexys A7, **Open Hardware Manager → Auto Connect → Program Device**.
3. Подключить PS/2 клавиатуру к разъёму USB HID (порт `J1` на плате).
4. При нажатии клавиш на семисегментниках отобразится скан-код: hex0 = младший ниббл, hex1 = старший.

---

## Ключевые особенности реализации

### sys_clk_rst_gen — делитель тактовой частоты

Модуль принимает 100 МГц с генератора FPGA и выдаёт 10 МГц для всей процессорной системы. `resetn_i` (активный низкий, кнопка BTNL/BTNR) инвертируется в `rst` (активный высокий) для ядра.

### PS2Receiver — приём по протоколу PS/2

Модуль `PS2Receiver` содержит `debouncer` для подавления дребезга линий клавиатуры. Принимает 11-битный фрейм (start + 8 бит данных + parity + stop), выдаёт байт и строб `rx_valid`. `ps2_sb_ctrl` фиксирует байт в регистре, выставляет `interrupt_request_o = 1` (сигнал прерывания) и держит его до записи в регистр сброса.

### irq_pending — защита от повторного прерывания

В `lab_10.irq.sv` реализован лatch `irq_pending`: после первого `trap` он блокирует повторное срабатывание до прихода `mret`. Это важно, так как `mie` остаётся ненулевым в течение всего выполнения обработчика.

### Условие разрешения прерываний

`lab_10.irq.sv` проверяет `mie_i` — **однобитный** вход от `processor_core`. Прошивка (`program.mem`) выполняет `csrw mie, 1` (устанавливает бит 0), что обеспечивает `mie_i = 1`.
