/* ASCAM-1 firmware main loop: read command lines from the UART and run them. */
#include "hal.h"
#include "proto.h"

static experiment_t exp_state;

int main(void)
{
    char line[128];
    unsigned len = 0;
    hal_init();
    proto_init(&exp_state);
    hal_uart_puts("ASCAM-1 fw " FW_VERSION " ready (synthetic keys only)\n");
    for (;;) {
        int c = hal_uart_getc();
        if (c < 0) {
#ifdef ASCAM_HOST
            if (hal_input_closed()) return 0;
#endif
            continue;
        }
        if (c == '\n' || c == '\r') {
            line[len] = 0;
            if (len) proto_handle_line(&exp_state, line, hal_uart_puts);
            len = 0;
        } else if (len < sizeof line - 1) {
            line[len++] = (char)c;
        }
    }
}
