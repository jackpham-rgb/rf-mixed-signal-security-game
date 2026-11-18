/* AES-128 encryption (FIPS-197), used only as a synthetic workload whose power
 * draw depends on a test key. Not a hardened implementation. */
#ifndef ASCAM_AES128_H
#define ASCAM_AES128_H
#include <stdint.h>

typedef struct { uint8_t rk[176]; } aes128_ctx;

void aes128_init(aes128_ctx *ctx, const uint8_t key[16]);
void aes128_encrypt(const aes128_ctx *ctx, const uint8_t in[16], uint8_t out[16]);

#endif
