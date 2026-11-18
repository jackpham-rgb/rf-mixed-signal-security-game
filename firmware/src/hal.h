/* Hardware interface. hal/stm32g431 implements it for the board; hal/host
 * implements it on a PC for tests and the simulator. */
#ifndef ASCAM_HAL_H
#define ASCAM_HAL_H
#include <stdint.h>

#define GATE_WORD_US 1u   /* one gating word per microsecond (TIM6 at 1 MHz) */

void hal_init(void);
/* Switch the system clock (24 or 32 MHz) and retune every clock-derived output:
 * MCO (branch 1/2 carriers), TIM16 250 kHz (branch 0), TIM3 ~6 MHz (branch 3). */
int hal_set_clock_mhz(uint8_t mhz);
uint8_t hal_clock_mhz(void);
void hal_trigger(int high);
/* Stream n words to GPIOB->BSRR, one per microsecond, driving EN0..EN3. */
void hal_gating_start(const uint32_t *words, uint16_t n);
void hal_gating_stop(void);          /* stops streaming and turns all branches off */
void hal_delay_us(uint32_t us);
int hal_uart_getc(void);             /* -1 when nothing is waiting */
void hal_uart_puts(const char *s);

#ifdef ASCAM_HOST
/* Host build only: event log for tests, and end-of-input detection. */
typedef enum { EV_CLOCK, EV_TRIGGER, EV_GATE_START, EV_GATE_STOP, EV_DELAY } hal_event_kind;
typedef struct { hal_event_kind kind; uint32_t value; } hal_event;
int hal_input_closed(void);
const hal_event *hal_host_events(int *n);
void hal_host_reset_events(void);
const uint32_t *hal_host_last_gate(uint16_t *n);
#endif

#endif
