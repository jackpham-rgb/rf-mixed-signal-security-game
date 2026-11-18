/* Line-based ASCII command protocol over the UART (115200 8N1).
 *
 *   ID                          -> OK ASCAM-1 fw <version>
 *   HELP                        -> list of commands
 *   SEED <n>                    reseed the RNG (also resets the trace counter)
 *   KEY <0|1> <32 hex chars>    synthetic key used when the secret bit S is 0 or 1
 *   DEF <id> <24|32> <l0><l1><l2><l3>   defense id (0-7): clock MHz and loads,
 *                               each load 0 (off), 1 (on), or R (random gating)
 *   WEIGHT <id> <w>             mixed policy weight of defense id (0 = never)
 *   CLEAR                       all weights to 0
 *   GATE <us> | LEAD <us> | GAP <us>    timing of each trace
 *   STATUS                      current settings
 *   RUN <n>                     run n traces; prints one line per trace:
 *                               T <index> <def> <S> <plaintext hex> <ciphertext hex>
 *                               then DONE <n>
 * Every command answers with a line starting OK or ERR.
 */
#ifndef ASCAM_PROTO_H
#define ASCAM_PROTO_H
#include "experiment.h"

#define FW_VERSION "0.1.0"

typedef void (*writer_fn)(const char *s);

void proto_init(experiment_t *e);
void proto_handle_line(experiment_t *e, const char *line, writer_fn out);

#endif
