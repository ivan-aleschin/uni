#include "protocol.h"

uint64_t calculate_partial(uint64_t start, uint64_t end, uint64_t mod) {
    uint64_t result = 1;
    for (uint64_t i = start; i <= end; i++) {
        result = (result * i) % mod;
    }
    return result;
}