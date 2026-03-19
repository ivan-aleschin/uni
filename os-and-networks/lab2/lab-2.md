
---
# Task 1

**Описание:**
- **Как меняются значения переменных через указатели:**  
    В функцию передаются адреса переменных, по этим адресам можно менять значения.
- **Почему нельзя просто `void Swap(char a, char b)`?**  
    Потому что передаются копии, а не оригиналы — изменения не сохранятся.

**swap.c**
```c
#include "swap.h"

void Swap(char *a, char *b) {
    char tmp = *a;
    *a = *b;
    *b = tmp;
}
```

**swap.h**
```c
#ifndef SWAP_H
#define SWAP_H

void Swap(char *a, char *b);

#endif
```

**main.c**
```c
#include <stdio.h>
#include "swap.h"

int main() {
    char a = 'a';
    char b = 'b';
    Swap(&a, &b);
    printf("%c %c\n", a, b);
    return 0;
}
```

**Компиляция**
```bash
gcc main.c swap.c -o swap_demo
./swap_demo
# Ожидаемый вывод: b a
```

**Вывод**
```bash
b a
```

---
# Task 2

**Описание:**
- Программа получает строку как аргумент командной строки (`argv[1]`).
- Копирует её в новую память (`strdup`).
- Вызывает `RevertString`, которая переворачивает строку на месте.
- Выводит результат и освобождает память.
- **Зачем выделять память под строку?**  
    Аргументы командной строки в C — константные строки, их нельзя изменять напрямую.
    
- **Что такое стек и куча?**
    
    - _Стек_: для локальных переменных, память освобождается при выходе из функции.
    - _Куча_: для динамического выделения (`malloc`/`free`), память живёт до явного освобождения.
- **Как устроены аргументы командной строки?**  
    `main(int argc, char *argv[])` — argc: количество аргументов, argv: массив строк.

**revert_string.c**
```c
#include "revert_string.h"
#include <stdlib.h>
#include <string.h>

void RevertString(char *str) {
    if (!str) return;
    int len = strlen(str);
    for (int i = 0; i < len / 2; ++i) {
        char tmp = str[i];
        str[i] = str[len - 1 - i];
        str[len - 1 - i] = tmp;
    }
}
```

**revert_string.h**
```c
#ifndef REVERT_STRING_H
#define REVERT_STRING_H

void RevertString(char *str);

#endif
```

**main.c**
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "revert_string.h"

int main(int argc, char *argv[]) {
    if (argc < 2) {
        printf("Usage: %s <string>\n", argv[0]);
        return 1;
    }
    char *str = strdup(argv[1]);
    RevertString(str);
    printf("%s\n", str);
    free(str);
    return 0;
}
```

**Компиляция**
```bash
gcc main.c revert_string.c -o revert_demo
./revert_demo hello
# Ожидаемый вывод: olleh
```

**Вывод**
```bash
olleh
```

---
# Task 3

**Описание:**
- **Что такое статическая библиотека?**  
    Файл `.a`, содержимое включается в исполняемый файл.
- **Что такое динамическая библиотека?**  
    Файл `.so`, подключается при запуске программы.
- **Что делают опции компилятора?**
    - `-c` — компиляция без линковки.
    - `-fPIC` — генерация позиционно-независимого кода (для .so).
    - `-shared` — создать .so.
    - `-L.` — искать библиотеки в текущей папке.
    - `-lrevert_string` — использовать librevert_string.so или .a.
- **Что такое LD_LIBRARY_PATH?**  
    Переменная окружения, где искать динамические библиотеки при запуске.

**Static lib**
```bash
gcc -c revert_string.c -o revert_string.o
ar rcs librevert_string.a revert_string.o
gcc main.c librevert_string.a -o revert_static
```

**Dynamic lib**
```bash
gcc -fPIC -c revert_string.c -o revert_string.o
gcc -shared -o librevert_string.so revert_string.o
gcc main.c -L. -lrevert_string -o revert_dynamic
```

**Компиляция**
```bash
export LD_LIBRARY_PATH=.
./revert_dynamic hello
# Ожидаемый вывод: olleh
```

```bash
olleh
```

---
# Task 4

**Описание:**
- **Для чего нужен LD_LIBRARY_PATH?**  
    Чтобы динамический линковщик нашёл нужную библиотеку при запуске теста.
- **Почему нельзя использовать другую .so?**  
    Тесты должны проверять ровно ту реализацию, что используется в приложении.
- **Что такое CUnit?**  
    Фреймворк для написания и запуска unit-тестов на C.
- **Как тесты устроены?**  
    Каждый тест вызывает функцию, сравнивает результат с ожидаемым (`CU_ASSERT_STRING_EQUAL_FATAL`).

**tests.c**
```C
#include <CUnit/Basic.h>
#include <stdio.h>
#include <string.h>
#include "revert_string.h"

void testRevertString(void) {
  char simple_string[] = "Hello";
  char str_with_spaces[] = "String with spaces";
  char str_with_odd_chars_num[] = "abc";
  char str_with_even_chars_num[] = "abcd";

  RevertString(simple_string);
  CU_ASSERT_STRING_EQUAL_FATAL(simple_string, "olleH");

  RevertString(str_with_spaces);
  CU_ASSERT_STRING_EQUAL_FATAL(str_with_spaces, "secaps htiw gnirtS");

  RevertString(str_with_odd_chars_num);
  CU_ASSERT_STRING_EQUAL_FATAL(str_with_odd_chars_num, "cba");

  RevertString(str_with_even_chars_num);
  CU_ASSERT_STRING_EQUAL_FATAL(str_with_even_chars_num, "dcba");
}

int main() {
  CU_pSuite pSuite = NULL;
  /* initialize the CUnit test registry */

  if (CUE_SUCCESS != CU_initialize_registry()) return CU_get_error();
  /* add a suite to the registry */

  pSuite = CU_add_suite("Suite", NULL, NULL);
  if (NULL == pSuite) {

    CU_cleanup_registry();
    return CU_get_error();

  }
  /* add the tests to the suite */

  /* NOTE - ORDER IS IMPORTANT - MUST TEST fread() AFTER fprintf() */

  if ((NULL == CU_add_test(pSuite, "test of RevertString function",
                           testRevertString))) {

    CU_cleanup_registry();
    return CU_get_error();
  }

  /* Run all tests using the CUnit Basic interface */
  CU_basic_set_mode(CU_BRM_VERBOSE);
  CU_basic_run_tests();
  CU_cleanup_registry();
  return CU_get_error();

}
```

**Компиляция**
```bash
gcc tests.c -I../revert_string -L../revert_string -lrevert_string -lcunit -o tests
```

```bash
export LD_LIBRARY_PATH=../revert_string
./tests
```

**Вывод**
```bash
Suite: Suite
  Test: test of RevertString function ...passed

Run Summary:    Type  Total    Ran Passed Failed Inactive
              suites      1      1    n/a      0        0
               tests      1      1      1      0        0
             asserts      4      4      4      0      n/a

Elapsed time =    0.000 seconds
```

---

# Вопросы по теории

1. **Разница между стеком и кучей**
    
    - **Стек** — область памяти для временного хранения локальных переменных и возврата из функций, выделение и освобождение происходит автоматически.
    - **Куча** — область памяти для динамического выделения по запросу через `malloc`/`free`, управление вручную.
2. **Аргументы командной строки**
    
    - Передаются в `main(int argc, char *argv[])`, где `argv[1]` — первый аргумент пользователя.
    - Пример: `./prog arg1 arg2`
3. **Статическая и динамическая линковка**
    
    - **Статическая** — код библиотеки встраивается в исполняемый файл (`.a`).
    - **Динамическая** — код библиотеки подгружается при запуске (`.so`).
4. **Опции компилятора**
    
    - `-I<dir>` — добавить путь к заголовочным файлам
    - `-L<dir>` — добавить путь к библиотекам
    - `-l<name>` — линковаться с библиотекой
    - `-shared` — создать динамическую библиотеку
    - `-o <file>` — имя выходного файла
    - `-c` — только компиляция без линковки
    - `-fPIC` — подготовка кода для динамической библиотеки
5. **ar** — утилита для создания статических библиотек (`ar rcs libfoo.a foo.o`)
    
6. **LD_LIBRARY_PATH** — переменная окружения для поиска динамических библиотек при запуске.