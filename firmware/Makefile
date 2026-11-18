# ASCAM-1 firmware
#   make test   build and run the host tests (gcc)
#   make sim    build the host simulator (same firmware, stdin/stdout as UART)
#   make fw     cross-compile for the STM32G431 (arm-none-eabi-gcc)

CORE = src/aes128.c src/rng.c src/experiment.c src/proto.c
BUILD = build
WARN = -Wall -Wextra -Werror -std=c11

HOST_CC ?= gcc
HOST_FLAGS = $(WARN) -O2 -DASCAM_HOST

ARM_CC = arm-none-eabi-gcc
ARM_OBJCOPY = arm-none-eabi-objcopy
ARM_SIZE = arm-none-eabi-size
MCU = -mcpu=cortex-m4 -mthumb -mfpu=fpv4-sp-d16 -mfloat-abi=hard
ARM_FLAGS = $(WARN) $(MCU) -Os -ffunction-sections -fdata-sections -DSTM32G431xx \
            -Ithird_party/cmsis_core -Ithird_party/cmsis_device_g4 -Isrc
ARM_LD = -Thal/stm32g431/stm32g431cb.ld -Wl,--gc-sections -specs=nano.specs -specs=nosys.specs \
         -Wl,-Map=$(BUILD)/ascam1.map

.PHONY: all test sim fw clean
all: test sim fw

$(BUILD):
	mkdir -p $(BUILD)

$(BUILD)/test_core: $(CORE) hal/host/hal_host.c tests/test_core.c | $(BUILD)
	$(HOST_CC) $(HOST_FLAGS) -o $@ $^

test: $(BUILD)/test_core
	./$(BUILD)/test_core

sim: $(BUILD)/ascam_sim
$(BUILD)/ascam_sim: $(CORE) src/main.c hal/host/hal_host.c | $(BUILD)
	$(HOST_CC) $(HOST_FLAGS) -o $@ $^

fw: $(BUILD)/ascam1.bin
$(BUILD)/ascam1.elf: $(CORE) src/main.c hal/stm32g431/hal_stm32.c hal/stm32g431/syscalls.c third_party/cmsis_device_g4/startup_stm32g431xx.s | $(BUILD)
	$(ARM_CC) $(ARM_FLAGS) $(ARM_LD) -o $@ $^
$(BUILD)/ascam1.bin: $(BUILD)/ascam1.elf
	$(ARM_OBJCOPY) -O binary $< $@
	$(ARM_SIZE) $<

clean:
	rm -rf $(BUILD)
