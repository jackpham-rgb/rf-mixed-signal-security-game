# ASCAM-1 firmware

Firmware for the ASCAM-1 test board (`hardware/`). It runs a synthetic AES-128
workload, pulses a scope trigger around each encryption, and applies the defense
chosen for each trace: clock hop (32 or 24 MHz) and on, off, or randomly gated
dummy loads. A PC script drives it over a serial port and labels every trace.

Status: **builds and passes its tests; not yet run on hardware** (the board has
not been built). Synthetic keys only.

## How one trace works

1. Pick a defense from the mixed policy (weights you set).
2. Switch the clock if needed. Timers and MCO are retuned automatically; the UART
   runs from the 16 MHz internal oscillator, so the baud rate never changes.
3. Pick the secret bit S at random, and a random plaintext. Key = key[S].
4. Start the gating: DMA streams one word per microsecond into GPIOB, turning
   EN0 to EN3 on, off, or random (branch 0 bits last 5 us, the others 1 us).
5. Wait `LEAD` us, raise the trigger (SMA J2), run AES, drop the trigger.
6. Stop the gating (all loads off), print one line, wait `GAP` us for the scope.

## Layout

| Path | What |
|---|---|
| `src/` | Portable core: AES-128, RNG, gating patterns, policy sampling, trace loop, serial protocol, main loop |
| `hal/stm32g431/` | Board layer: clock/PLL hop, TIM16 + TIM3 carriers, MCO, TIM6-triggered DMA gating, USART2, linker script |
| `hal/host/` | PC layer: stdin/stdout as the UART, plus an event log the tests check |
| `tests/test_core.c` | Host tests: FIPS-197 AES vectors, gating patterns, policy frequencies, the order of hardware actions in a trace, the protocol |
| `host/ascam_ctl.py` | PC control script: runs a plan, verifies every ciphertext with an independent AES, writes `traces.csv` and `run.json` |
| `host/plans/` | One plan per measurement step in `hardware/README.md` |
| `third_party/` | ST CMSIS device files for STM32G4 and ARM CMSIS core headers (Apache-2.0, licenses included) |

## Build and test

```bash
cd firmware
make test        # host tests (gcc)
make sim         # the same firmware as a PC program, for trying plans without a board
make fw          # cross-compile for the STM32G431: build/ascam1.elf and .bin (arm-none-eabi-gcc)
python -m pytest host
```

The board image is about 15.5 KB of flash and 4.7 KB of RAM.

## Flashing and running

1. Connect an ST-Link to J4 (Tag-Connect TC2030-NL cable), and a 3.3 V USB-serial
   adapter to J6 (pin 1 GND, pin 2 board TX, pin 3 board RX).
2. Flash `build/ascam1.bin` at 0x08000000, for example with STM32CubeProgrammer
   or `st-flash write build/ascam1.bin 0x08000000`.
3. Open the serial port at 115200 8N1 and type `ID`. It should answer
   `OK ASCAM-1 fw 0.1.0`.
4. Run a plan while the scope captures on the J2 trigger:

```bash
python firmware/host/ascam_ctl.py --port COM5 --plan firmware/host/plans/leakage.json --out captures/leakage
```

Row i of `captures/leakage/traces.csv` belongs to the i-th triggered capture.
Try any plan first without a board: replace `--port COM5` with
`--sim firmware/build/ascam_sim`.

## Serial commands

| Command | Effect |
|---|---|
| `ID`, `HELP`, `STATUS` | identify, list commands, show settings and the active policy |
| `SEED <n>` | reseed the random generator (same seed gives the same traces) |
| `KEY <0\|1> <32 hex>` | synthetic key used when S = 0 or 1 |
| `DEF <id> <24\|32> <4 of 0/1/R>` | defense id 0 to 7: clock and the four loads (off, on, random) |
| `WEIGHT <id> <w>`, `CLEAR` | mixed-policy weights |
| `GATE <us>`, `LEAD <us>`, `GAP <us>` | gating window, lead before the trigger, idle time between traces |
| `RUN <n>` | run n traces; prints `T <index> <defense> <S> <plaintext> <ciphertext>` per trace, then `DONE <n>` |

## Check before the first power-up

These come from the datasheet tables and could not be tested without the chip:

- Alternate functions: PA6 AF1 = TIM16_CH1, PB0 AF2 = TIM3_CH3, PA8 AF0 = MCO,
  PA2/PA3 AF7 = USART2 (STM32G431 datasheet, pin table). The firmware uses
  TIM16 for PA6 because TIM3 cannot run 250 kHz on CH1 and 6 MHz on CH3 at the
  same time.
- PLL settings: 8 MHz HSE / 2 x 48 / 6 = 32 MHz and / 2 x 36 / 6 = 24 MHz (VCO 192
  and 144 MHz, inside the allowed range).
- `GATE` must cover `LEAD` plus the AES time. Measure the trigger pulse width on
  the scope once and adjust `GATE` if needed (default 256 us).
- At 115200 baud each trace line takes about 7 ms to print, so 10,000 traces take
  roughly 90 s.
