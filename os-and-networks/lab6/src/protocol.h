#ifndef PROTOCOL_H
#define PROTOCOL_H

#include <stdint.h>

#if defined(__APPLE__)
#include <libkern/OSByteOrder.h>
#define htobe64(x) OSSwapHostToBigInt64(x)
#define be64toh(x) OSSwapBigToHostInt64(x)
#elif defined(__linux__)
#include <endian.h>
#endif

// Структура задания для сервера
typedef struct {
    uint64_t start;  // Начало диапазона
    uint64_t end;    // Конец диапазона
    uint64_t mod;    // Модуль
} Task;

// Структура ответа от сервера
typedef struct {
    uint64_t result; // Результат вычислений
} Response;

// Вычисление частичного произведения по модулю
uint64_t calculate_partial(uint64_t start, uint64_t end, uint64_t mod);

#endif // PROTOCOL_H