#include "Number.h"

Number operator+(const Number &d1, const Number &d2) {
    return Number(((d1._num * d2._denom) + (d2._num * d1._denom)), (d1._denom * d2._denom));
}

Number operator-(const Number &d1, const Number &d2) {
    return Number(((d1._num * d2._denom) - (d2._num * d1._denom)), (d1._denom * d2._denom));
}

Number operator*(const Number &d1, const Number &d2) {
    return Number((d1._num * d2._num), (d1._denom * d2._denom));
}

Number operator/(const Number &d1, const Number &d2) {
    return Number((d1._num * d2._denom), (d1._denom * d2._num));
}

Number operator<(const Number &d1, const Number &d2) {
    if ((d1._num * d2._denom) > (d1._denom * d2._num)) {
        return Number(d1._num,d1._denom);
    } else {
        return Number(d2._num,d2._denom);
    }
}