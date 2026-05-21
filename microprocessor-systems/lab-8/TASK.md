# Оригинальное задание — ЛР14 «Высокоуровневое программирование»

> Источник: репозиторий APS (Architectures of Processor Systems), МИЭТ  
> https://github.com/MPSU/APS/tree/master/Labs/14.%20Programming

**Вариант:** Алешин Иван Кириллович → Клавиатура PS/2 → Семисегментники (`ps2_hex`)

---

## Цель

Написать программу для индивидуального задания на языке C, скомпилировать кросс-компилятором под архитектуру rv32i и запустить на процессоре RISC-V из ЛР7/ЛР9/ЛР11.

---

## Задание

Написать программу для варианта из ЛР4/ЛР13 на языке C (или C++).

Программа обязательно должна содержать две функции:
- `main` — точка входа, вызывается после исполнения `.boot`-секции startup-файла
- `int_handler` — обработчик прерывания, вызывается при каждом запросе прерывания от контроллера устройства ввода

### Требования к реализации

- Доступ к регистрам периферии — через указатели на структуры из `platform.h`
- При работе с PS/2: помнить что отправляется скан-код клавиши, при отпускании — `0xF0` + повторный скан-код
- Функция `main` может быть пустой (стартап-файл содержит бесконечный цикл после `main`)
- Нельзя использовать `printf`/`scanf`, динамические массивы, STL — стандартные библиотеки не подключены

### Алгоритм для варианта ps2_hex

1. По прерыванию от PS/2: читать `scan_code` из `ps2_ptr->scan_code`
2. Записать `hex0 = scan_code & 0xF` (младший ниббл)
3. Записать `hex1 = (scan_code >> 4) & 0xF` (старший ниббл)
4. Сбросить флаг PS/2: `ps2_ptr->rst = 1`

---

## Порядок выполнения

1. Обновить `memory_pkg.sv`: `INSTR_MEM_SIZE_BYTES = 1024`, `DATA_MEM_SIZE_BYTES = 2048`
2. Написать `main.c` с функциями `main` и `int_handler`
3. Скомпилировать объектные файлы:
   ```bash
   riscv32-none-elf-gcc -c -march=rv32i_zicsr -mabi=ilp32 startup.S -o startup.o
   riscv32-none-elf-gcc -c -march=rv32i_zicsr -mabi=ilp32 -O2 -ffreestanding -nostdlib main.c -o main.o
   ```
4. Скомпоновать:
   ```bash
   riscv32-none-elf-gcc -march=rv32i_zicsr -mabi=ilp32 \
     -Wl,--gc-sections -nostartfiles -T linker_script.ld \
     startup.o main.o -o result.elf
   ```
5. Экспортировать секции для инициализации памяти:
   ```bash
   riscv32-none-elf-objcopy -O verilog --verilog-data-width=4 -j .text result.elf init_instr.mem
   riscv32-none-elf-objcopy -O verilog --verilog-data-width=4 -j .data -j .bss -j .sdata result.elf init_data.mem
   # Удалить строку @XXXXXXXX из init_data.mem (LMA-адрес, не нужен симулятору)
   sed -i '/^@/d' init_data.mem
   ```
6. Добавить `init_instr.mem` и `init_data.mem` в проект Vivado как Simulation Sources
7. Проверить симуляцию через тестбенч из ЛР13 (обновить с нужными входными данными)
8. Проверить работу на ПЛИС с ЛР13

---

## Соглашение о вызовах (calling convention RISC-V)

| Регистр | ABI Name | Описание | Сохраняет |
|---|---|---|---|
| x0 | zero | Всегда 0 | — |
| x1 | ra | Return address | Caller |
| x2 | sp | Stack pointer | Callee |
| x3 | gp | Global pointer | — |
| x5–7 | t0–2 | Temporaries | Caller |
| x8–9 | s0–1/fp | Saved / frame pointer | Callee |
| x10–11 | a0–1 | Args / return values | Caller |
| x12–17 | a2–7 | Args | Caller |
| x18–27 | s2–11 | Saved registers | Callee |
| x28–31 | t3–6 | Temporaries | Caller |

**Callee-saved** регистры (s0–s11, sp) — вызванная функция обязана восстановить их значение перед возвратом.  
**Caller-saved** регистры (t*, a*) — вызывающая функция сама сохраняет, если они нужны после вызова.

---

## Скрипт компоновщика (linker_script.ld) — ключевые моменты

- `instr_mem`: origin=0, length=1K — память инструкций
- `data_mem`: origin=0, length=2K — память данных (адреса перекрываются с instr_mem, но физически разные)
- Секция `.data` имеет LMA=`0x00800000` — компоновщик размещает по высокому адресу, при экспорте `init_data.mem` строку `@20000000` нужно удалить
- `_stack_size = 640` — программный стек (8 вложенных вызовов)
- `_trap_stack_size = 640` — стек обработчика прерываний

---

## Стартап-файл (startup.S) — что делает

1. Инициализирует `gp` (global pointer) и `sp` (stack pointer)
2. Зануляет `.bss`-секцию (неинициализированные статические переменные)
3. Настраивает `mtvec` (адрес `_int_handler`), `mscratch` (указатель на стек прерываний), `mie` (все прерывания разрешены)
4. Вызывает `main`
5. Уходит в бесконечный цикл

`_int_handler` (asm-обёртка):
- Меняет местами `sp` и `mscratch` (переключается на стек прерываний)
- Сохраняет caller-saved регистры + CSR на стек
- Вызывает `int_handler` (C-функция)
- Восстанавливает контекст
- Выполняет `mret`
