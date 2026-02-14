#!/bin/bash

echo "================================================================================="
echo "Лабораторная работа №4 - Полное выполнение всех заданий (ИСПРАВЛЕННАЯ ВЕРСИЯ)"
echo "GitHub Codespaces (2 ядра, 8 GB RAM)"
echo "================================================================================="

# Создаем директорию для выводов
mkdir -p test_outputs
LOG_FILE="test_outputs/lab4_complete_log.txt"
exec > >(tee -a "$LOG_FILE") 2>&1

echo "Время начала: $(date)"
echo "Количество ядер: $(nproc)"
echo ""

# Проверяем наличие необходимых файлов
echo "Проверка необходимых файлов..."
MISSING_FILES=()
for file in parallel_min_max.c process_memory.c parallel_sum.c sum.c sum.h; do
    if [ ! -f "$file" ]; then
        MISSING_FILES+=("$file")
    fi
done

if [ ${#MISSING_FILES[@]} -ne 0 ]; then
    echo "[ERROR] Отсутствуют файлы: ${MISSING_FILES[*]}"
    exit 1
fi

echo "[SUCCESS] Все необходимые файлы присутствуют"

echo ""
echo "---------------------------------------------------------------------------------"
echo "СОЗДАНИЕ ОТСУТСТВУЮЩИХ ФАЙЛОВ"
echo "---------------------------------------------------------------------------------"

# Создаем zombie.c если отсутствует
if [ ! -f "zombie.c" ]; then
    echo "Создание zombie.c..."
    cat > zombie.c << 'EOF'
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/wait.h>

int main() {
    printf("Демонстрация зомби-процессов\n");
    printf("Создание дочернего процесса...\n");
    
    pid_t pid = fork();
    
    if (pid == 0) {
        // Дочерний процесс
        printf("Дочерний процесс (PID: %d) запущен\n", getpid());
        printf("Дочерний процесс завершается через 2 секунды...\n");
        sleep(2);
        printf("Дочерний процесс завершен\n");
        exit(0);
    } else if (pid > 0) {
        // Родительский процесс
        printf("Родительский процесс (PID: %d) создал дочерний %d\n", getpid(), pid);
        printf("Родительский процесс засыпает на 10 секунд...\n");
        printf("В это время выполните в другом терминале:\n");
        printf("ps aux | grep %d\n", pid);
        printf("чтобы увидеть зомби-процесс (статус Z)\n\n");
        
        sleep(10); // Даем время увидеть зомби
        
        printf("\nРодительский процесс просыпается и вызывает wait()...\n");
        int status;
        wait(&status);
        printf("Зомби-процесс убран (wait вернул статус: %d)\n", status);
    } else {
        perror("fork failed");
        return 1;
    }
    
    printf("Программа завершена\n");
    return 0;
}
EOF
    echo "[SUCCESS] zombie.c создан"
fi

# Создаем Makefile если отсутствует
if [ ! -f "Makefile" ]; then
    echo "Создание Makefile..."
    cat > Makefile << 'EOF'
# Makefile для лабораторной работы №4
CC = gcc
CFLAGS = -Wall -Wextra -std=c99
PTHREAD_FLAGS = -pthread

# Все цели
ALL_TARGETS = parallel_min_max process_memory parallel_sum zombie

all: $(ALL_TARGETS)

# Задание 1: Программа с timeout
parallel_min_max: parallel_min_max.c
	$(CC) $(CFLAGS) -o $@ $<

# Задание 3: Анализ памяти процесса
process_memory: process_memory.c
	$(CC) $(CFLAGS) -o $@ $<

# Задание 2: Демонстрация зомби-процессов
zombie: zombie.c
	$(CC) $(CFLAGS) -o $@ $<

# Задание 5-6: Параллельное суммирование с pthreads
parallel_sum: parallel_sum.o sum.o
	$(CC) $(CFLAGS) $(PTHREAD_FLAGS) -o $@ $^

parallel_sum.o: parallel_sum.c sum.h
	$(CC) $(CFLAGS) $(PTHREAD_FLAGS) -c parallel_sum.c

sum.o: sum.c sum.h
	$(CC) $(CFLAGS) $(PTHREAD_FLAGS) -c sum.c

clean:
	rm -f $(ALL_TARGETS) *.o

.PHONY: all clean
EOF
    echo "[SUCCESS] Makefile создан"
fi

echo ""
echo "---------------------------------------------------------------------------------"
echo "ЗАДАНИЕ 4 и 6: ПРОВЕРКА MAKEFILE"
echo "---------------------------------------------------------------------------------"

echo "Очистка и сборка через Makefile..."
make clean
make

if [ $? -eq 0 ]; then
    echo "[SUCCESS] Сборка через Makefile завершена успешно"
    echo "Собранные программы:"
    for prog in parallel_min_max process_memory parallel_sum zombie; do
        if [ -f "$prog" ]; then
            echo "✓ $prog"
        else
            echo "✗ $prog (отсутствует)"
        fi
    done
else
    echo "[ERROR] Ошибка сборки через Makefile"
    exit 1
fi

echo ""
echo "---------------------------------------------------------------------------------"
echo "ЗАДАНИЕ 1: УПРАВЛЕНИЕ ПРОЦЕССАМИ И СИГНАЛЫ"
echo "---------------------------------------------------------------------------------"

echo "Теория:"
echo "- kill() - отправка сигнала процессу"
echo "- waitpid() с WNOHANG - неблокирующее ожидание" 
echo "- alarm() + SIGALRM - установка таймера"
echo "- signal() - установка обработчика сигнала"

echo ""
echo "Тест 1: Запуск с timeout (5 секунд)"
./parallel_min_max --timeout 5 > test_outputs/task1_timeout.txt 2>&1

echo "Анализ выполнения:"
if grep -q "Timeout reached" test_outputs/task1_timeout.txt; then
    echo "[SUCCESS] Таймаут сработал корректно"
else
    echo "[WARNING] Таймаут не сработал"
fi

if grep -q "завершен по сигналу: 9" test_outputs/task1_timeout.txt; then
    echo "[SUCCESS] Процессы завершены по SIGKILL"
else
    echo "[WARNING] Процессы завершены не по SIGKILL"
fi

echo ""
echo "Вывод программы:"
cat test_outputs/task1_timeout.txt

echo ""
echo "---------------------------------------------------------------------------------"
echo "ЗАДАНИЕ 2: ЗОМБИ-ПРОЦЕССЫ"
echo "---------------------------------------------------------------------------------"

echo "Теория:"
echo "- Зомби-процессы: завершенные процессы, ожидающие чтения статуса родителем"
echo "- Появляются когда родитель не вызывает wait() после завершения потомка"
echo "- Исчезают когда родитель вызывает wait() или завершается сам"
echo "- Опасны: занимают записи в таблице процессов"

echo ""
echo "Запуск демонстрации зомби-процессов в фоне..."
./zombie > test_outputs/task2_output.txt 2>&1 &
ZOMBIE_PID=$!

echo "Ожидание создания зомби-процесса..."
sleep 3

# Ищем дочерний процесс
CHILD_PID=$(ps --ppid $ZOMBIE_PID -o pid= 2>/dev/null | head -1 | tr -d ' ')

if [ -n "$CHILD_PID" ]; then
    echo "Найден дочерний процесс: $CHILD_PID"
    echo "Проверка состояния процесса:"
    ps -o pid,state,command -p $CHILD_PID 2>/dev/null
    
    if ps -o state -p $CHILD_PID 2>/dev/null | grep -q "Z"; then
        echo "[SUCCESS] Обнаружен зомби-процесс (статус Z)"
    else
        echo "[INFO] Процесс не в статусе зомби (возможно еще выполняется)"
    fi
else
    echo "[WARNING] Дочерний процесс не найден"
fi

echo "Ожидание завершения программы zombie..."
wait $ZOMBIE_PID 2>/dev/null

echo ""
echo "Вывод программы:"
cat test_outputs/task2_output.txt

echo ""
echo "---------------------------------------------------------------------------------"
echo "ЗАДАНИЕ 3: АНАЛИЗ ВИРТУАЛЬНОЙ ПАМЯТИ"
echo "---------------------------------------------------------------------------------"

echo "Теория:"
echo "- etext: конец сегмента кода (исполняемые инструкции)"
echo "- edata: конец сегмента инициализированных данных"
echo "- end: конец сегмента BSS (неинициализированных данных)"

echo ""
echo "Запуск анализа сегментов памяти..."
./process_memory > test_outputs/task3_output.txt 2>&1

echo "[SUCCESS] Программа завершена"
echo ""
echo "Вывод программы:"
cat test_outputs/task3_output.txt

echo ""
echo "---------------------------------------------------------------------------------"
echo "ЗАДАНИЕ 5: ПАРАЛЛЕЛЬНОЕ СУММИРОВАНИЕ"
echo "---------------------------------------------------------------------------------"

echo "Теория:"
echo "- pthread_create(): создание потоков"
echo "- pthread_join(): ожидание завершения потоков"
echo "- Потоки разделяют память процесса"

echo ""
echo "Тест 1: Базовые аргументы (2 потока, 10,000 элементов)"
./parallel_sum --threads_num 2 --seed 123 --array_size 10000 > test_outputs/task5_test1.txt 2>&1
echo "Результат:"
tail -3 test_outputs/task5_test1.txt

echo ""
echo "Тест 2: Сравнение производительности"
echo "Размер массива: 100,000 элементов"
echo ""
printf "%-12s | %-12s | %-15s\n" "Потоки" "Время (сек)" "Сумма"
echo "-------------+--------------+-----------------"

for threads in 1 2 4; do
    ./parallel_sum --threads_num $threads --seed 42 --array_size 100000 > "test_outputs/threads_$threads.txt" 2>&1
    TIME_TAKEN=$(grep "Time taken" "test_outputs/threads_$threads.txt" | awk '{print $3}')
    TOTAL_SUM=$(grep "Total sum" "test_outputs/threads_$threads.txt" | awk '{print $3}')
    printf "%-12d | %-12.6f | %-15d\n" "$threads" "$TIME_TAKEN" "$TOTAL_SUM"
done

echo ""
echo "---------------------------------------------------------------------------------"
echo "ФИНАЛЬНАЯ ПРОВЕРКА"
echo "---------------------------------------------------------------------------------"

echo "Проверка целостности сборки..."
make clean
make > /dev/null 2>&1

if [ $? -eq 0 ]; then
    echo "[SUCCESS] Финальная сборка успешна"
    echo ""
    echo "Все программы собраны:"
    for prog in parallel_min_max process_memory parallel_sum zombie; do
        if [ -f "$prog" ]; then
            echo "✓ $prog"
        else
            echo "✗ $prog"
        fi
    done
else
    echo "[ERROR] Ошибка финальной сборки"
fi

echo ""
echo "---------------------------------------------------------------------------------"
echo "ОЧИСТКА"
echo "---------------------------------------------------------------------------------"

echo "Удаление временных файлов..."
rm -rf test_outputs
make clean