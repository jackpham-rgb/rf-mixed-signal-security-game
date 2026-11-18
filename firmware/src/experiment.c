#include "experiment.h"
#include "aes128.h"
#include "hal.h"

static uint32_t gate_buf[MAX_GATE_WORDS];

void experiment_defaults(experiment_t *e)
{
    for (int i = 0; i < MAX_DEFS; i++) {
        e->defs[i].clk_mhz = 32;
        for (int b = 0; b < N_BRANCH; b++) e->defs[i].load[b] = LOAD_OFF;
        e->weight[i] = 0;
    }
    e->weight[0] = 1;              /* default policy: defense 0 = no defense */
    for (int i = 0; i < 16; i++) {
        e->key[0][i] = (uint8_t)i;                 /* 000102...0f */
        e->key[1][i] = (uint8_t)(0xf0 | i);        /* f0f1...ff   */
    }
    e->seed = 126;
    rng_seed(&e->rng, e->seed);
    e->gate_us = 256;
    e->lead_us = 8;
    e->gap_us = 1000;
}

int experiment_pick_def(experiment_t *e)
{
    uint32_t total = 0;
    for (int i = 0; i < MAX_DEFS; i++) total += e->weight[i];
    if (total == 0) return -1;
    uint32_t x = rng_below(&e->rng, total);
    for (int i = 0; i < MAX_DEFS; i++) {
        if (x < e->weight[i]) return i;
        x -= e->weight[i];
    }
    return -1;   /* unreachable */
}

size_t gating_build(uint32_t *words, size_t n, const defense_t *d, rng_t *r)
{
    uint8_t bit[N_BRANCH] = {0};
    for (size_t k = 0; k < n; k++) {
        uint32_t w = 0;
        for (int b = 0; b < N_BRANCH; b++) {
            if (d->load[b] == LOAD_ON) bit[b] = 1;
            else if (d->load[b] == LOAD_OFF) bit[b] = 0;
            else if (b != 0 || k % BRANCH0_BIT_WORDS == 0) bit[b] = (uint8_t)(rng_next(r) & 1u);
            /* BSRR: low half sets a pin, high half resets it */
            w |= bit[b] ? (1u << (EN_PIN0 + b)) : (1u << (EN_PIN0 + b + 16));
        }
        words[k] = w;
    }
    return n;
}

int experiment_run_trace(experiment_t *e, uint32_t index, trace_record_t *out)
{
    int di = experiment_pick_def(e);
    if (di < 0) return -1;
    const defense_t *d = &e->defs[di];
    if (hal_clock_mhz() != d->clk_mhz && hal_set_clock_mhz(d->clk_mhz) != 0) return -2;

    uint16_t n = e->gate_us > MAX_GATE_WORDS ? MAX_GATE_WORDS : e->gate_us;
    gating_build(gate_buf, n, d, &e->rng);

    out->index = index;
    out->def = (uint8_t)di;
    out->secret = (uint8_t)(rng_next(&e->rng) & 1u);
    for (int i = 0; i < 16; i += 4) {
        uint32_t x = rng_next(&e->rng);
        out->pt[i] = (uint8_t)x; out->pt[i + 1] = (uint8_t)(x >> 8);
        out->pt[i + 2] = (uint8_t)(x >> 16); out->pt[i + 3] = (uint8_t)(x >> 24);
    }
    aes128_ctx ctx;
    aes128_init(&ctx, e->key[out->secret]);   /* key schedule outside the trigger window */

    hal_gating_start(gate_buf, n);
    hal_delay_us(e->lead_us);
    hal_trigger(1);
    aes128_encrypt(&ctx, out->pt, out->ct);
    hal_trigger(0);
    hal_gating_stop();
    hal_delay_us(e->gap_us);
    return 0;
}
