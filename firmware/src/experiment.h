/* Experiment state: defense configurations, the mixed policy over them, the two
 * synthetic keys, and the trace loop. */
#ifndef ASCAM_EXPERIMENT_H
#define ASCAM_EXPERIMENT_H
#include <stddef.h>
#include <stdint.h>
#include "rng.h"

#define MAX_DEFS 8
#define N_BRANCH 4
#define MAX_GATE_WORDS 512
#define BRANCH0_BIT_WORDS 5   /* branch 0 random bits last 5 us (200 kHz), others 1 us */
#define EN_PIN0 4             /* EN0..EN3 on PB4..PB7 */

typedef enum { LOAD_OFF = 0, LOAD_ON = 1, LOAD_RANDOM = 2 } load_mode_t;

typedef struct {
    uint8_t clk_mhz;               /* 24 or 32: 24 is the "hop" */
    uint8_t load[N_BRANCH];        /* load_mode_t per branch */
} defense_t;

typedef struct {
    defense_t defs[MAX_DEFS];
    uint16_t weight[MAX_DEFS];     /* mixed policy: P(def i) = weight[i] / sum */
    uint8_t key[2][16];            /* synthetic keys for secret bit S = 0 and 1 */
    rng_t rng;
    uint32_t seed;
    uint16_t gate_us;              /* gating window per trace (us) */
    uint16_t lead_us;              /* gating starts this long before the trigger */
    uint32_t gap_us;               /* idle time between traces (scope re-arm) */
} experiment_t;

typedef struct {
    uint32_t index;
    uint8_t def;
    uint8_t secret;
    uint8_t pt[16];
    uint8_t ct[16];
} trace_record_t;

void experiment_defaults(experiment_t *e);
int experiment_pick_def(experiment_t *e);   /* -1 if no defense has weight */
size_t gating_build(uint32_t *words, size_t n, const defense_t *d, rng_t *r);
/* Run one trace: pick a defense, apply clock and gating, encrypt, log. */
int experiment_run_trace(experiment_t *e, uint32_t index, trace_record_t *out);

#endif
