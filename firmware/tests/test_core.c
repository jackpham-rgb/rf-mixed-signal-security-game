/* Host tests for the portable firmware core. Build and run: make test */
#include <stdio.h>
#include <string.h>
#include "../src/aes128.h"
#include "../src/experiment.h"
#include "../src/hal.h"
#include "../src/proto.h"
#include "../src/rng.h"

static int failures, checks;
#define CHECK(cond) do { checks++; if (!(cond)) { failures++; \
    printf("FAIL %s:%d: %s\n", __FILE__, __LINE__, #cond); } } while (0)

static void unhex(const char *h, uint8_t *b) { for (int i = 0; i < 16; i++) sscanf(h + 2 * i, "%2hhx", &b[i]); }

static void test_aes_fips197(void)
{
    const char *vec[][3] = {   /* key, plaintext, ciphertext: FIPS-197 appendix C.1 and appendix B */
        {"000102030405060708090a0b0c0d0e0f", "00112233445566778899aabbccddeeff", "69c4e0d86a7b0430d8cdb78070b4c55a"},
        {"2b7e151628aed2a6abf7158809cf4f3c", "3243f6a8885a308d313198a2e0370734", "3925841d02dc09fbdc118597196a0b32"},
    };
    for (int v = 0; v < 2; v++) {
        uint8_t k[16], p[16], c[16], out[16];
        unhex(vec[v][0], k); unhex(vec[v][1], p); unhex(vec[v][2], c);
        aes128_ctx ctx;
        aes128_init(&ctx, k);
        aes128_encrypt(&ctx, p, out);
        CHECK(memcmp(out, c, 16) == 0);
    }
}

static void test_rng(void)
{
    rng_t a, b;
    rng_seed(&a, 7); rng_seed(&b, 7);
    for (int i = 0; i < 100; i++) CHECK(rng_next(&a) == rng_next(&b));
    int hist[5] = {0};
    for (int i = 0; i < 50000; i++) { uint32_t x = rng_below(&a, 5); CHECK(x < 5); hist[x]++; }
    for (int i = 0; i < 5; i++) CHECK(hist[i] > 9500 && hist[i] < 10500);
}

static int pin_set(uint32_t w, int b) { return (w >> (EN_PIN0 + b)) & 1u; }
static int pin_reset(uint32_t w, int b) { return (w >> (EN_PIN0 + b + 16)) & 1u; }

static void test_gating(void)
{
    static uint32_t w[4000];
    rng_t r; rng_seed(&r, 3);
    defense_t d = {32, {LOAD_RANDOM, LOAD_ON, LOAD_OFF, LOAD_RANDOM}};
    gating_build(w, 4000, &d, &r);
    int ones1 = 0, ones3 = 0;
    for (int k = 0; k < 4000; k++) {
        for (int b = 0; b < 4; b++) CHECK(pin_set(w[k], b) + pin_reset(w[k], b) == 1);   /* each pin driven once */
        CHECK(pin_set(w[k], 1) == 1);                  /* ON branch stays on */
        CHECK(pin_reset(w[k], 2) == 1);                /* OFF branch stays off */
        if (k % BRANCH0_BIT_WORDS) CHECK(pin_set(w[k], 0) == pin_set(w[k - 1], 0));   /* 5 us bits */
        ones3 += pin_set(w[k], 3);
        ones1 += pin_set(w[k], 0);
        CHECK((w[k] & ~(0xF0u | 0xF00000u)) == 0);     /* only PB4..PB7 touched */
    }
    CHECK(ones3 > 1800 && ones3 < 2200);               /* random branch on about half the time */
    CHECK(ones1 > 1700 && ones1 < 2300);
}

static void test_policy_weights(void)
{
    experiment_t e;
    experiment_defaults(&e);
    e.weight[0] = 1; e.weight[3] = 3;
    int c0 = 0, c3 = 0, other = 0;
    for (int i = 0; i < 20000; i++) {
        int d = experiment_pick_def(&e);
        if (d == 0) c0++; else if (d == 3) c3++; else other++;
    }
    CHECK(other == 0);
    CHECK(c0 > 4400 && c0 < 5600);
    for (int i = 0; i < 8; i++) e.weight[i] = 0;
    CHECK(experiment_pick_def(&e) == -1);
}

static void test_trace_sequence(void)
{
    experiment_t e;
    hal_init();
    experiment_defaults(&e);
    e.defs[0].clk_mhz = 24;                            /* force a hop on the first trace */
    hal_host_reset_events();
    trace_record_t r;
    CHECK(experiment_run_trace(&e, 0, &r) == 0);
    int n;
    const hal_event *ev = hal_host_events(&n);
    hal_event_kind want[] = {EV_CLOCK, EV_GATE_START, EV_DELAY, EV_TRIGGER, EV_TRIGGER, EV_GATE_STOP, EV_DELAY};
    CHECK(n == 7);
    for (int i = 0; i < 7 && i < n; i++) CHECK(ev[i].kind == want[i]);
    CHECK(ev[0].value == 24);
    CHECK(ev[3].value == 1 && ev[4].value == 0);       /* trigger high, then low */
    CHECK(ev[2].value == e.lead_us);
    /* the logged ciphertext is AES(key[S], plaintext) */
    aes128_ctx ctx; uint8_t ct[16];
    aes128_init(&ctx, e.key[r.secret]);
    aes128_encrypt(&ctx, r.pt, ct);
    CHECK(memcmp(ct, r.ct, 16) == 0);
    /* second trace at the same clock: no clock switch */
    hal_host_reset_events();
    CHECK(experiment_run_trace(&e, 1, &r) == 0);
    ev = hal_host_events(&n);
    CHECK(ev[0].kind == EV_GATE_START);
}

static char outbuf[65536];
static void capture(const char *s) { strncat(outbuf, s, sizeof outbuf - strlen(outbuf) - 1); }
static int count_lines(const char *prefix)
{
    int c = 0; size_t L = strlen(prefix);
    for (const char *p = outbuf; *p; p = strchr(p, '\n') + 1) { if (!strncmp(p, prefix, L)) c++; if (!strchr(p, '\n')) break; }
    return c;
}

static void test_protocol(void)
{
    experiment_t e;
    hal_init();
    proto_init(&e);
    outbuf[0] = 0;
    proto_handle_line(&e, "id", capture);
    CHECK(strstr(outbuf, "OK ASCAM-1 fw") == outbuf);
    outbuf[0] = 0;
    proto_handle_line(&e, "DEF 1 24 R01x", capture);
    CHECK(!strncmp(outbuf, "ERR", 3));
    outbuf[0] = 0;
    proto_handle_line(&e, "DEF 9 32 0000", capture);
    CHECK(!strncmp(outbuf, "ERR", 3));
    outbuf[0] = 0;
    proto_handle_line(&e, "DEF 1 24 R0R1", capture);
    CHECK(!strcmp(outbuf, "OK\n"));
    CHECK(e.defs[1].clk_mhz == 24 && e.defs[1].load[0] == LOAD_RANDOM && e.defs[1].load[3] == LOAD_ON);
    proto_handle_line(&e, "KEY 1 2b7e151628aed2a6abf7158809cf4f3c", capture);
    CHECK(e.key[1][0] == 0x2b && e.key[1][15] == 0x3c);
    proto_handle_line(&e, "WEIGHT 1 2", capture);
    proto_handle_line(&e, "GAP 0", capture);
    outbuf[0] = 0;
    proto_handle_line(&e, "SEED 5", capture);
    proto_handle_line(&e, "RUN 50", capture);
    CHECK(count_lines("T ") == 50);
    CHECK(count_lines("DONE 50") == 1);
    char first[65536];
    strcpy(first, outbuf);
    outbuf[0] = 0;
    proto_handle_line(&e, "SEED 5", capture);
    proto_handle_line(&e, "RUN 50", capture);
    CHECK(strcmp(first, outbuf) == 0);                 /* same seed, same traces */
    outbuf[0] = 0;
    proto_handle_line(&e, "FLY", capture);
    CHECK(!strncmp(outbuf, "ERR", 3));
    outbuf[0] = 0;
    proto_handle_line(&e, "CLEAR", capture);
    proto_handle_line(&e, "RUN 1", capture);
    CHECK(strstr(outbuf, "ERR no defense has weight") != NULL);
}

int main(void)
{
    test_aes_fips197();
    test_rng();
    test_gating();
    test_policy_weights();
    test_trace_sequence();
    test_protocol();
    printf("%d checks, %d failures\n", checks, failures);
    return failures ? 1 : 0;
}
