/* PC implementation of the HAL: stdin/stdout stand in for the UART, and every
 * hardware action is appended to an event log that the tests inspect. */
#include <stdio.h>
#include <string.h>
#include "../../src/hal.h"

#define MAX_EVENTS 4096
static hal_event events[MAX_EVENTS];
static int n_events;
static uint8_t clock_mhz;
static int input_closed;
static uint32_t last_gate[512];
static uint16_t last_gate_n;

static void log_ev(hal_event_kind k, uint32_t v)
{
    if (n_events < MAX_EVENTS) events[n_events++] = (hal_event){k, v};
}

void hal_init(void) { clock_mhz = 32; n_events = 0; }
int hal_set_clock_mhz(uint8_t mhz)
{
    if (mhz != 24 && mhz != 32) return -1;
    clock_mhz = mhz;
    log_ev(EV_CLOCK, mhz);
    return 0;
}
uint8_t hal_clock_mhz(void) { return clock_mhz; }
void hal_trigger(int high) { log_ev(EV_TRIGGER, (uint32_t)high); }
void hal_gating_start(const uint32_t *w, uint16_t n)
{
    last_gate_n = n > 512 ? 512 : n;
    memcpy(last_gate, w, last_gate_n * sizeof *w);
    log_ev(EV_GATE_START, n);
}
void hal_gating_stop(void) { log_ev(EV_GATE_STOP, 0); }
void hal_delay_us(uint32_t us) { log_ev(EV_DELAY, us); }
int hal_uart_getc(void)
{
    int c = getchar();
    if (c == EOF) { input_closed = 1; return -1; }
    return c;
}
void hal_uart_puts(const char *s) { fputs(s, stdout); fflush(stdout); }
int hal_input_closed(void) { return input_closed; }
const hal_event *hal_host_events(int *n) { *n = n_events; return events; }
void hal_host_reset_events(void) { n_events = 0; }
const uint32_t *hal_host_last_gate(uint16_t *n) { *n = last_gate_n; return last_gate; }
