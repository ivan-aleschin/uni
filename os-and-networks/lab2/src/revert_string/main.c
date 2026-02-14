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