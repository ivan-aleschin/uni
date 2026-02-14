# Лабораторная работа №5: POSIX Threads и синхронизация

**Автор:** AleshinIvan  
**Дата:** 2025-11-21

## Описание

Лабораторная работа посвящена изучению многопоточного программирования с использованием POSIX threads (pthreads) и механизмов синхронизации.

### Темы

- Race Condition (состояние гонки)
- Critical Section (критическая секция)
- Mutex (взаимное исключение)
- Deadlock (взаимная блокировка)
- Параллельные вычисления

## Структура проекта

```
lab5/
├── src/
│   ├── mutex.c              # Задание 1: демонстрация race condition
│   ├── mutex_with_lock.c    # Задание 1: использование мьютекса
│   ├── factorial.c          # Задание 2: параллельный факториал
│   ├── deadlock.c           # Задание 3: демонстрация deadlock
│   └── deadlock_fixed.c     # Задание 3: решение deadlock
├── .gitignore
└── README.md
```

## Компиляция

Все программы компилируются с флагом `-pthread`:

```bash
cd lab5/src

# Задание 1
gcc -o mutex_without mutex.c -pthread
gcc -o mutex_with mutex_with_lock.c -pthread

# Задание 2
gcc -o factorial factorial.c -pthread

# Задание 3
gcc -o deadlock deadlock.c -pthread
gcc -o deadlock_fixed deadlock_fixed.c -pthread
```

## Запуск

### Задание 1: Race Condition vs Mutex

**Без мьютекса (некорректный результат):**
```bash
./mutex_without
# Ожидаемо: counter = 100
# Реально: counter = 51 (или другое число < 100)
```

**С мьютексом (корректный результат):**
```bash
./mutex_with
# Результат: counter = 100 ✓
```

**Объяснение:**  
Без мьютекса два потока конкурируют за общую переменную `common`, что приводит к потере обновлений (race condition). Мьютекс обеспечивает атомарность операции инкремента.

### Задание 2: Параллельное вычисление факториала

```bash
./factorial -k <число> --pnum=<потоки> --mod=<модуль>
```

**Примеры:**

```bash
# 10! mod 10 с 4 потоками
./factorial -k 10 --p
