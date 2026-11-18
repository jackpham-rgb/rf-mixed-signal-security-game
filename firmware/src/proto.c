#include "proto.h"
#include <ctype.h>
#include <stdio.h>
#include <string.h>
#include "hal.h"

static uint32_t trace_counter;

void proto_init(experiment_t *e)
{
    experiment_defaults(e);
    trace_counter = 0;
}

static int parse_u32(const char *s, uint32_t *v)
{
    if (!s || !*s) return -1;
    uint32_t x = 0;
    for (; *s; s++) {
        if (!isdigit((unsigned char)*s)) return -1;
        if (x > 429496729u) return -1;
        x = x * 10u + (uint32_t)(*s - '0');
    }
    *v = x;
    return 0;
}

static int hexval(char c)
{
    if (c >= '0' && c <= '9') return c - '0';
    c = (char)tolower((unsigned char)c);
    if (c >= 'a' && c <= 'f') return c - 'a' + 10;
    return -1;
}

static void hex16(char *dst, const uint8_t b[16])
{
    static const char H[] = "0123456789abcdef";
    for (int i = 0; i < 16; i++) { dst[2 * i] = H[b[i] >> 4]; dst[2 * i + 1] = H[b[i] & 15]; }
    dst[32] = 0;
}

#define MAX_TOK 8
static int split(char *buf, char *tok[])
{
    int n = 0;
    for (char *p = strtok(buf, " \t\r\n"); p && n < MAX_TOK; p = strtok(NULL, " \t\r\n")) tok[n++] = p;
    return n;
}

static void err(writer_fn out, const char *msg)
{
    char b[96];
    snprintf(b, sizeof b, "ERR %s\n", msg);
    out(b);
}

void proto_handle_line(experiment_t *e, const char *line, writer_fn out)
{
    char buf[128], msg[160];
    char *t[MAX_TOK];
    uint32_t a, v;
    strncpy(buf, line, sizeof buf - 1);
    buf[sizeof buf - 1] = 0;
    int n = split(buf, t);
    if (n == 0) return;
    for (char *p = t[0]; *p; p++) *p = (char)toupper((unsigned char)*p);

    if (!strcmp(t[0], "ID")) {
        out("OK ASCAM-1 fw " FW_VERSION "\n");
    } else if (!strcmp(t[0], "HELP")) {
        out("OK ID HELP SEED KEY DEF WEIGHT CLEAR GATE LEAD GAP STATUS RUN\n");
    } else if (!strcmp(t[0], "SEED")) {
        if (n != 2 || parse_u32(t[1], &v)) return err(out, "usage: SEED <n>");
        e->seed = v;
        rng_seed(&e->rng, v);
        trace_counter = 0;
        out("OK\n");
    } else if (!strcmp(t[0], "KEY")) {
        if (n != 3 || parse_u32(t[1], &a) || a > 1 || strlen(t[2]) != 32)
            return err(out, "usage: KEY <0|1> <32 hex chars>");
        uint8_t k[16];
        for (int i = 0; i < 16; i++) {
            int hi = hexval(t[2][2 * i]), lo = hexval(t[2][2 * i + 1]);
            if (hi < 0 || lo < 0) return err(out, "key must be hex");
            k[i] = (uint8_t)(hi << 4 | lo);
        }
        memcpy(e->key[a], k, 16);
        out("OK\n");
    } else if (!strcmp(t[0], "DEF")) {
        if (n != 4 || parse_u32(t[1], &a) || a >= MAX_DEFS || parse_u32(t[2], &v) || (v != 24 && v != 32)
            || strlen(t[3]) != N_BRANCH)
            return err(out, "usage: DEF <0-7> <24|32> <4 of 0/1/R>");
        defense_t d = { .clk_mhz = (uint8_t)v };
        for (int b = 0; b < N_BRANCH; b++) {
            char c = (char)toupper((unsigned char)t[3][b]);
            if (c == '0') d.load[b] = LOAD_OFF;
            else if (c == '1') d.load[b] = LOAD_ON;
            else if (c == 'R') d.load[b] = LOAD_RANDOM;
            else return err(out, "loads must be 0, 1 or R");
        }
        e->defs[a] = d;
        out("OK\n");
    } else if (!strcmp(t[0], "WEIGHT")) {
        if (n != 3 || parse_u32(t[1], &a) || a >= MAX_DEFS || parse_u32(t[2], &v) || v > 65535)
            return err(out, "usage: WEIGHT <0-7> <0-65535>");
        e->weight[a] = (uint16_t)v;
        out("OK\n");
    } else if (!strcmp(t[0], "CLEAR")) {
        for (int i = 0; i < MAX_DEFS; i++) e->weight[i] = 0;
        out("OK\n");
    } else if (!strcmp(t[0], "GATE") || !strcmp(t[0], "LEAD") || !strcmp(t[0], "GAP")) {
        if (n != 2 || parse_u32(t[1], &v)) return err(out, "usage: GATE|LEAD|GAP <us>");
        if (!strcmp(t[0], "GATE")) {
            if (v == 0 || v > MAX_GATE_WORDS) return err(out, "GATE must be 1-512 us");
            e->gate_us = (uint16_t)v;
        } else if (!strcmp(t[0], "LEAD")) {
            if (v >= e->gate_us) return err(out, "LEAD must be shorter than GATE");
            e->lead_us = (uint16_t)v;
        } else {
            e->gap_us = v;
        }
        out("OK\n");
    } else if (!strcmp(t[0], "STATUS")) {
        snprintf(msg, sizeof msg, "OK seed=%lu clk=%u gate=%u lead=%u gap=%lu traces=%lu\n",
                 (unsigned long)e->seed, (unsigned)hal_clock_mhz(), e->gate_us, e->lead_us,
                 (unsigned long)e->gap_us, (unsigned long)trace_counter);
        out(msg);
        for (int i = 0; i < MAX_DEFS; i++) {
            if (!e->weight[i]) continue;
            const char L[] = "01R";
            snprintf(msg, sizeof msg, "OK def %d clk=%u loads=%c%c%c%c weight=%u\n", i, e->defs[i].clk_mhz,
                     L[e->defs[i].load[0]], L[e->defs[i].load[1]], L[e->defs[i].load[2]], L[e->defs[i].load[3]],
                     e->weight[i]);
            out(msg);
        }
    } else if (!strcmp(t[0], "RUN")) {
        if (n != 2 || parse_u32(t[1], &v) || v == 0) return err(out, "usage: RUN <n>");
        out("OK\n");
        for (uint32_t i = 0; i < v; i++) {
            trace_record_t r;
            int rc = experiment_run_trace(e, trace_counter, &r);
            if (rc == -1) return err(out, "no defense has weight");
            if (rc != 0) return err(out, "clock switch failed");
            char pt[33], ct[33];
            hex16(pt, r.pt);
            hex16(ct, r.ct);
            snprintf(msg, sizeof msg, "T %lu %u %u %s %s\n", (unsigned long)r.index, r.def, r.secret, pt, ct);
            out(msg);
            trace_counter++;
        }
        snprintf(msg, sizeof msg, "DONE %lu\n", (unsigned long)v);
        out(msg);
    } else {
        err(out, "unknown command (try HELP)");
    }
}
