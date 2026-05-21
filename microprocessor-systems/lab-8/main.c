#include "platform.h"
#include <stdint.h>

/* Вариант ps2_hex: по прерыванию от PS/2 клавиатуры читаем scan-код и
   выводим его на семисегментные дисплеи: hex0 = младший ниббл, hex1 = старший. */

void int_handler(void)
{
    uint32_t code = ps2_ptr->scan_code;
    hex_ptr->hex0 = code & 0xFu;
    hex_ptr->hex1 = (code >> 4) & 0xFu;
    ps2_ptr->rst = 1u;
}

int main(void)
{
    while (1) { }
    return 0;
}
