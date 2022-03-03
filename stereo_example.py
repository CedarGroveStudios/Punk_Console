## SPDX-FileCopyrightText: 2022 Cedar Grove Maker Studios
# SPDX-License-Identifier: MIT

# cedargrove_punk_console.stereo_example.py v1.0

# Tested on an RP2040 Feather using CircuitPython v7.1.1
# Waveform Output pins:
#   left channel: A1 (PWM digital output, not analog DAC output)
#   right channel: D13 (PWM digital output)
# Oscillator Frequency Input pin: A2 (analog input)
# One-Shot Multivibrator Pulse Width Input pin: A3 (analog input)

import board
import analogio
import pwmio
from simpleio import map_range
from cedargrove_punk_console import PunkConsole

# instantiate a PunkConsole output on pin A1 and D13
punk_console_l = PunkConsole(board.A1)
punk_console_r = PunkConsole(board.D13)

f_in = analogio.AnalogIn(board.A2)  # Oscillator Frequency
pw_in = analogio.AnalogIn(board.A3)  # One-Shot Pulse Width

while True:
    # read the inputs, map to practical audio ranges, send to PunkConsole instances
    #   oscillator frequency range: 3Hz to 3kHz
    #   one-shot pulse width range: 0.5ms to 5ms
    punk_console_l.frequency = map_range(f_in.value, 0, 65535, 3, 3000)
    punk_console_l.pulse_width_ms = map_range(pw_in.value, 0, 65535, 0.5, 5.0)

    # invert the output ranges for the right-channel output
    punk_console_r.frequency = map_range(f_in.value, 0, 65535, 3000, 3)
    punk_console_r.pulse_width_ms = map_range(pw_in.value, 0, 65535, 5.0, 0.5)
