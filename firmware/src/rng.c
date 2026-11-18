#include "rng.h"

void rng_seed(rng_t *r, uint32_t seed) { r->s = seed ? seed : 0x9e3779b9u; }

uint32_t rng_next(rng_t *r)
{
    uint32_t x = r->s;
    x ^= x << 13; x ^= x >> 17; x ^= x << 5;
    return r->s = x;
}

uint32_t rng_below(rng_t *r, uint32_t n)
{
    uint32_t limit = UINT32_MAX - (UINT32_MAX % n);   /* rejection: no modulo bias */
    uint32_t x;
    do { x = rng_next(r); } while (x >= limit);
    return x % n;
}
