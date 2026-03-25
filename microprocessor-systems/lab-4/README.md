# Лабораторная работа №4 — Простейшее программируемое устройство (CYBERcobra)

## Цель
Собрать процессор CYBERcobra, объединив ранее разработанные модули:
- память инструкций (`instr_mem`)
- регистровый файл (`register_file`)
- АЛУ (`alu`)
- 32-битный сумматор (`fulladder32`)
- счётчик команд (PC) и управляющую логику

---

## Структура файлов

```
lab-4/
├── design.sv               # модуль CYBERcobra
├── memory_pkg.sv           # размеры памяти
├── alu_opcodes_pkg.sv      # опкоды АЛУ
├── lab1_adders.sv          # сумматоры из ЛР1
├── lab2_alu.sv             # АЛУ из ЛР2
├── testbench.sv            # локальный тестбенч с waveform
├── lab_04.tb_cybercobra.sv # официальный тест
├── program.mem             # бинарная программа (HEX для $readmemh)
├── program.txt             # исходник программы для cyberconverter
└── README.md
```

> `design.sv` находится в этой папке и содержит модуль `CYBERcobra`.

---

## Сигнатура модуля

```
module CYBERcobra (
  input  logic         clk_i,
  input  logic         rst_i,
  input  logic [15:0]  sw_i,
  output logic [31:0]  out_o
);
endmodule
```

---

## Пайплайн №1 — Проверка дома (iverilog + GTKWave)

### Шаг 1. Компиляция и запуск

```bash
iverilog -g2012 -o sim \
  memory_pkg.sv \
  alu_opcodes_pkg.sv \
  lab1_adders.sv \
  lab2_alu.sv \
  design.sv \
  testbench.sv && vvp sim
```

> Если `memory_pkg.sv` и `alu_opcodes_pkg.sv` лежат в другой папке — добавь их в команду компиляции или скопируй в `lab-4/`.

### Шаг 2. Просмотр waveform

```bash
gtkwave wave.vcd
```

В GTKWave добавь внутренние сигналы `pc_q`, `instr`, `ws`, `bit_b`, `bit_j`, `rf_we`, `offset_raw`, `rf_const_raw`, `ra1`, `ra2`, `wa`, `rf_wd`, `alu_result`, `alu_flag`, `pc_addend`, `pc_sum` и отследи работу процессора по тактам.

---

## Пайплайн №2 — Проверка в Vivado

### Шаг 1. Создать проект
1. **File → Project → New → RTL Project**
2. **Design Sources**:
   - `design.sv`
   - `lab1_adders.sv`
   - `lab2_alu.sv`
   - `memory_pkg.sv`
   - `alu_opcodes_pkg.sv`
3. **Simulation Sources**:
   - `lab_04.tb_cybercobra.sv`
4. **Add Files**:
   - `program.mem`

### Шаг 2. Симуляция
- В **Simulation Sources** выбрать `lab_04_tb_CYBERcobra` как top
- **Run Behavioral Simulation**

### Шаг 3. Проверка работы
В этой лабе **нет автоматического PASS/FAIL**.  
Нужно вручную анализировать waveform:
- какое значение PC сейчас
- какая инструкция читается
- что записывается в регистровый файл
- как изменяется PC после выполнения

### Шаг 4. Синтез и прошивка ПЛИС
1. В **Design Sources** установи `CYBERcobra` как top (правый клик → **Set as Top**).
2. **Flow → Run Synthesis**
3. **Flow → Run Implementation**
4. **Flow → Generate Bitstream**
5. Подключи плату и выбери **Program Device**

### Что показать на защите
- Временную диаграмму с корректной работой `PC`, `instr`, `rf_we` и итоговым `out_o`
- Успешную симуляцию без ошибок
- (Если требуется) работающую прошивку на плате

---

## Что должно работать

- **Вычислительные инструкции** → запись результата АЛУ в регистр
- **Загрузка константы** → запись `rf_const` в регистр
- **Загрузка с внешних устройств** → запись `sw_i` в регистр
- **Условные переходы** → PC меняется только если `flag == 1`
- **Безусловные переходы** → PC всегда смещается
- При инструкциях перехода `WE = 0`

---

## Подсказка по инициализации

Для варианта 1 (циклический сдвиг вправо) выбрана простая константа `a = 11` (`0x0000000B`), чтобы было легко проверить результат вручную.
Вход `sw_i` в `testbench.sv` установлен как в примере — `2`.

Ожидаемый результат:
- `k = sw_i & 31 = 2`
- `out_o = (a >> k) | (a << (32 - k)) = 0xC0000002`

Исходник программы лежит в `program.txt`.  
Файл `program.mem` сгенерирован из него (формат HEX для `$readmemh`).