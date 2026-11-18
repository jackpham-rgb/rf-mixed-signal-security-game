/* xorshift32: small, fast, seedable. Drives the synthetic secrets, plaintexts,
 * defense choice, and random gating. Not cryptographically secure (it does not
 * need to be: everything it produces is logged). */
#ifndef ASCAM_RNG_H
#define ASCAM_RNG_H
#include <stdint.h>

typedef struct { uint32_t s; } rng_t;

void rng_seed(rng_t *r, uint32_t seed);
uint32_t rng_next(rng_t *r);
uint32_t rng_below(rng_t *r, uint32_t n);   /* uniform in [0, n), n > 0 */

#endif
