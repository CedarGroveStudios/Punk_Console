## SPDX-FileCopyrightText: 2022 Cedar Grove Maker Studios
# SPDX-License-Identifier: MIT

# cedargrove_punk_console.simple_example.py v1.0

import board
import analogio
import pwmio
from simpleio import map_range
from cedargrove_punk_console import PunkConsole

# instantiate a PunkConsole output on pin A1
punk_console = PunkConsole(board.A1)

# define the two potentiometer inputs
f_in = analogio.AnalogIn(board.A2)
pw_in = analogio.AnalogIn(board.A3)

while True:
    # read the inputs, map to practical audio ranges, send to PunkConsole instance
    punk_console.frequency = map_range(f_in.value, 0, 65535, 3, 3000)
    punk_console.pulse_width_ms = map_range(pw_in.value, 0, 65535, 0.5, 5.0)
