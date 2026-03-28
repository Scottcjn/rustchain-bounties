
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// SH4-specific optimizations
__attribute__((aligned(16)))
float frandr(float x) {
    return __builtin_frandr(x);
}

int main() {
    float x = 1.0;
    float y = frandr(x);
    printf("%f\n", y);
    return 0;
}
