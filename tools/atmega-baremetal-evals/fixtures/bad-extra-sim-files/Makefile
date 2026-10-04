# SPDX-License-Identifier: 0BSD
# Bare-metal avr-gcc Makefile. Targets: build size hex flash clean.
# No Arduino include or library paths on purpose: Arduino.h / Wire.h / SPI.h must fail to compile.
# On Windows without GNU make installed, run mingw32-make instead of make.
#
#   make MCU=atmega328p F_CPU=16000000UL
#   make flash PORT=<serial port>          (ISP programmers such as usbasp need no PORT)
#   make flash MCU=atmega4809 PORT=<serial port>
# Fuses and lock bits are never written by this Makefile.

MCU          ?= atmega4809
F_CPU        ?= 16000000UL
TARGET       ?= firmware
SRC          ?= main.c
BUILD_DIR    ?= build
EXTRA_CFLAGS ?=
AVRDUDE_FLAGS ?=
PORT         ?=

# megaAVR 0-series parts program over UPDI; all other parts over ISP.
UPDI_MCUS := atmega4808 atmega4809 atmega3208
ifneq ($(filter $(MCU),$(UPDI_MCUS)),)
PROGRAMMER ?= serialupdi
else
PROGRAMMER ?= usbasp
endif
# avrdude part id: atmega328p -> m328p, atmega2560 -> m2560, atmega4809 -> m4809
AVRDUDE_PART ?= m$(patsubst atmega%,%,$(MCU))

CFLAGS  = -mmcu=$(MCU) -DF_CPU=$(F_CPU) -std=gnu11 -Os -g -Wall -Wextra \
          -ffunction-sections -fdata-sections -MMD -MP $(EXTRA_CFLAGS)
LDFLAGS = -mmcu=$(MCU) -Wl,--gc-sections

OBJ := $(addprefix $(BUILD_DIR)/,$(notdir $(SRC:.c=.o)))
vpath %.c $(sort $(dir $(SRC)))

ifeq ($(wildcard $(BUILD_DIR)),)
$(shell mkdir $(BUILD_DIR))
endif

# cmd.exe has no rm; a POSIX sh on PATH (e.g. from Git for Windows) does.
CLEAN = rm -rf $(BUILD_DIR) $(TARGET).hex
ifeq ($(OS),Windows_NT)
ifneq ($(COMSPEC),)
ifneq ($(findstring $(COMSPEC),$(shell echo %COMSPEC%)),)
CLEAN = -if exist $(BUILD_DIR) rmdir /s /q $(BUILD_DIR) & if exist $(TARGET).hex del $(TARGET).hex
endif
endif
endif

.PHONY: build size hex flash clean
build: hex size
hex: $(TARGET).hex

$(BUILD_DIR)/%.o: %.c
	avr-gcc $(CFLAGS) -c $< -o $@

$(BUILD_DIR)/$(TARGET).elf: $(OBJ)
	avr-gcc $(LDFLAGS) $^ -o $@

# -R .eeprom keeps EEMEM initialisers out of the flash image.
$(TARGET).hex: $(BUILD_DIR)/$(TARGET).elf
	avr-objcopy -O ihex -R .eeprom $< $@

size: $(BUILD_DIR)/$(TARGET).elf
	avr-size $<

flash: $(TARGET).hex
ifeq ($(PROGRAMMER)$(PORT),serialupdi)
	$(error PORT is required for serialupdi, e.g. make flash PORT=<serial port>)
endif
	avrdude -c $(PROGRAMMER) -p $(AVRDUDE_PART) $(if $(PORT),-P $(PORT)) $(AVRDUDE_FLAGS) -U flash:w:$(TARGET).hex:i

clean:
	$(CLEAN)

-include $(OBJ:.o=.d)
