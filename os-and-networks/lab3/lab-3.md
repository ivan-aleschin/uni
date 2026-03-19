
# task-1


**Описание**

- Аргументы командной строки — это параметры, которые программа получает при запуске. Программа ожидает два аргумента: seed и размер массива.
- Компиляторы gcc/clang переводят исходный код (`.c` файлы) в исполняемые файлы. Сборка программы `sequential_min_max` из исходника и object-файлов.

**find_min_max.c**
```C
struct MinMax GetMinMax(int *array, unsigned int begin, unsigned int end) {
  struct MinMax min_max;
  min_max.min = INT_MAX;
  min_max.max = INT_MIN;
  for (unsigned int i = begin; i < end; i++) {
    if (array[i] < min_max.min) min_max.min = array[i];
    if (array[i] > min_max.max) min_max.max = array[i];
  }
  return min_max;
}
```

**Собираем и запускаем**
```bash
make sequential_min_max
./sequential_min_max 123 10
```
# task-2-3

**Описание**

- Здесь используется [getopt_long](https://man7.org/linux/man-pages/man3/getopt.3.html) для разбора аргументов вида `--seed=123 --array_size=100 --pnum=4 --by_files`. 
- `fork()` — создаёт новый процесс (дочерний), который копирует память родительского. Возвращает 0 в дочернем процессе, >0 — в родительском. Используется для параллельной обработки частей массива. Например, `--pnum=4` использует разделения массива на 4 части.
- `pipe()` — создаёт канал для обмена данными между процессами (родитель ↔ дочерний). Возвращает два файловых дескриптора: один для чтения, другой для записи. Дочерний процесс пишет min/max в pipe, родитель читает.
- Работа с файлами — через функции стандартной библиотеки: `fopen`, `fprintf`, `fscanf`, `fclose`. Используется для передачи результатов между процессами при опции `--by_files`.

**parallel_min_max.c**
```C
#include <ctype.h>
#include <limits.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

#include <sys/time.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <getopt.h>
#include <fcntl.h>

#include "find_min_max.h"
#include "utils.h"

int main(int argc, char **argv) {
  int seed = -1;
  int array_size = -1;
  int pnum = -1;
  bool with_files = false;

  while (true) {
    int current_optind = optind ? optind : 1;

    static struct option options[] = {{"seed", required_argument, 0, 0},
                                      {"array_size", required_argument, 0, 0},
                                      {"pnum", required_argument, 0, 0},
                                      {"by_files", no_argument, 0, 'f'},
                                      {0, 0, 0, 0}};

    int option_index = 0;
    int c = getopt_long(argc, argv, "f", options, &option_index);

    if (c == -1) break;

    switch (c) {
      case 0:
        switch (option_index) {
          case 0:
            seed = atoi(optarg);
            if (seed <= 0) {
              printf("seed must be positive\n");
              return 1;
            }
            break;
          case 1:
            array_size = atoi(optarg);
            if (array_size <= 0) {
              printf("array_size must be positive\n");
              return 1;
            }
            break;
          case 2:
            pnum = atoi(optarg);
            if (pnum <= 0) {
              printf("pnum must be positive\n");
              return 1;
            }
            break;
          case 3:
            with_files = true;
            break;

          default:
            printf("Index %d is out of options\n", option_index);
        }
        break;
      case 'f':
        with_files = true;
        break;

      case '?':
        break;

      default:
        printf("getopt returned character code 0%o?\n", c);
    }
  }

  if (optind < argc) {
    printf("Has at least one no option argument\n");
    return 1;
  }

  if (seed == -1 || array_size == -1 || pnum == -1) {
    printf("Usage: %s --seed \"num\" --array_size \"num\" --pnum \"num\" \n",
           argv[0]);
    return 1;
  }

  int *array = malloc(sizeof(int) * array_size);
  GenerateArray(array, array_size, seed);
  int active_child_processes = 0;

  struct timeval start_time;
  gettimeofday(&start_time, NULL);

  int pipefds[pnum][2];

  for (int i = 0; i < pnum; i++) {
    if (!with_files) {
      if (pipe(pipefds[i]) == -1) {
        perror("pipe");
        exit(1);
      }
    }
  }

  for (int i = 0; i < pnum; i++) {
    pid_t child_pid = fork();
    if (child_pid < 0) {
      printf("Fork failed!\n");
      free(array);
      return 1;
    }
    if (child_pid == 0) {
      // Child process
      unsigned int part_size = array_size / pnum;
      unsigned int start = i * part_size;
      unsigned int end = (i == pnum - 1) ? array_size : (i + 1) * part_size;

      struct MinMax min_max = GetMinMax(array, start, end);

      if (with_files) {
        char filename[256];
        sprintf(filename, "min_max_%d.txt", i);
        FILE *f = fopen(filename, "w");
        if (!f) {
          perror("fopen");
          exit(1);
        }
        fprintf(f, "%d %d", min_max.min, min_max.max);
        fclose(f);
      } else {
        close(pipefds[i][0]); // Close read
        write(pipefds[i][1], &min_max, sizeof(struct MinMax));
        close(pipefds[i][1]);
      }
      free(array);
      exit(0);
    }
    active_child_processes++;
  }

  // Parent process
  while (active_child_processes > 0) {
    wait(NULL);
    active_child_processes--;
  }

  struct MinMax min_max;
  min_max.min = INT_MAX;
  min_max.max = INT_MIN;

  for (int i = 0; i < pnum; i++) {
    int min = INT_MAX;
    int max = INT_MIN;
    if (with_files) {
      char filename[256];
      sprintf(filename, "min_max_%d.txt", i);
      FILE *f = fopen(filename, "r");
      if (!f) {
        perror("fopen read");
        continue;
      }
      fscanf(f, "%d %d", &min, &max);
      fclose(f);
      remove(filename);
    } else {
      close(pipefds[i][1]); // Close write
      struct MinMax child_min_max;
      read(pipefds[i][0], &child_min_max, sizeof(struct MinMax));
      close(pipefds[i][0]);
      min = child_min_max.min;
      max = child_min_max.max;
    }

    if (min < min_max.min) min_max.min = min;
    if (max > min_max.max) min_max.max = max;
  }

  struct timeval finish_time;
  gettimeofday(&finish_time, NULL);

  double elapsed_time = (finish_time.tv_sec - start_time.tv_sec) * 1000.0;
  elapsed_time += (finish_time.tv_usec - start_time.tv_usec) / 1000.0;

  free(array);

  printf("Min: %d\n", min_max.min);
  printf("Max: %d\n", min_max.max);
  printf("Elapsed time: %fms\n", elapsed_time);
  fflush(NULL);
  return 0;
}
```

**Собираем**
```bash
make parallel_min_max
```

**Запускаем через pipe**
```bash
./parallel_min_max --seed 123 --array_size 100 --pnum 4
```

**Запускаем через файлы**
```bash
./parallel_min_max --seed 123 --array_size 100 --pnum 4 --by_files
```
# task-4

**Описание**

- Makefile — набор правил для автоматизации сборки проектов.  Каждый `target` описывает, как получить файл (или действие). `make clean` — удаляет все бинарники и object-файлы.

**makefile**
```
# Компилятор и флаги
CC=gcc
CFLAGS=-I.

# Сборка последовательной версии
sequential_min_max : utils.o find_min_max.o utils.h find_min_max.h
	$(CC) -o sequential_min_max find_min_max.o utils.o sequential_min_max.c $(CFLAGS)

# Сборка параллельной версии
parallel_min_max : utils.o find_min_max.o utils.h find_min_max.h
	$(CC) -o parallel_min_max utils.o find_min_max.o parallel_min_max.c $(CFLAGS)

# Сборка файла с запуском через fork+exec (задание 5)
run_sequential : utils.o find_min_max.o utils.h find_min_max.h
	$(CC) -o run_sequential run_sequential.c find_min_max.o utils.o $(CFLAGS)

# Object-файлы
utils.o : utils.h
	$(CC) -o utils.o -c utils.c $(CFLAGS)

find_min_max.o : utils.h find_min_max.h
	$(CC) -o find_min_max.o -c find_min_max.c $(CFLAGS)

# Очистка бинарников и object-файлов
clean :
	rm -f utils.o find_min_max.o sequential_min_max parallel_min_max run_sequential
```


# task-5

**Описание**

- `exec` — семейство функций, которые заменяют текущий процесс на другой исполняемый файл.  Обычно вызывается в дочернем процессе после fork. Запуск другой программы из дочернего процесса.

**run_sequential.c**
```C
#include <stdio.h>
#include <stdlib.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <unistd.h>

// Пояснение: Эта программа принимает аргументы для запуска sequential_min_max
// и запускает её в дочернем процессе через fork+exec.

int main(int argc, char *argv[]) {
    // Проверяем, что введены все нужные аргументы для запуска sequential_min_max
    // (имя программы + seed + array_size)
    if (argc != 3) {
        printf("Usage: %s seed array_size\n", argv[0]);
        return 1;
    }

    pid_t pid = fork();

    if (pid < 0) {
        // Ошибка создания процесса
        perror("fork");
        return 1;
    }

    if (pid == 0) {
        // Дочерний процесс
        // Пояснение: Формируем массив аргументов для exec
        // Первый аргумент — имя исполняемого файла, затем seed и array_size
        char *args[4];
        args[0] = "./sequential_min_max"; // путь к программе
        args[1] = argv[1]; // seed
        args[2] = argv[2]; // array_size
        args[3] = NULL;    // завершающий NULL

        // Запускаем sequential_min_max с аргументами через execvp
        if (execvp(args[0], args) < 0) {
            perror("execvp");
            exit(1);
        }
        // execvp не возвращает, если успешно
    } else {
        // Родительский процесс
        // Ожидаем завершения дочернего и выводим его код выхода
        int status;
        waitpid(pid, &status, 0);

        if (WIFEXITED(status)) {
            printf("Child finished with code %d\n", WEXITSTATUS(status));
        } else {
            printf("Child terminated abnormally\n");
        }
    }
    return 0;
}
```

**Собираем**
```bash
make run_sequential
```

**Запускаем**
```bash
./run_sequential 123 10
```