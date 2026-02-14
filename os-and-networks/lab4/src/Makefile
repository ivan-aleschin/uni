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