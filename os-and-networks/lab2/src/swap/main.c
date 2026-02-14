#include <stdio.h>
#include "swap.h"

int main() {
    char a = 'a';
    char b = 'b';
    Swap(&a, &b);
    printf("%c %c\n", a, b);
    return 0;
}