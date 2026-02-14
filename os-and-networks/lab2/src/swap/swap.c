#include "swap.h"

void Swap(char *a, char *b) {
    char tmp = *a;
    *a = *b;
    *b = tmp;
}