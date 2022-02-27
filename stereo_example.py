## SPDX-FileCopyrightText: 2022 Cedar Grove Maker Studios
# SPDX-License-Identifier: MIT

# cedargrove_punk_console.stereo_example.py v1.0

import board
import analogio
import pwmio
from simpleio import map_range
from cedargrove_punk_console import PunkConsole

# instantiate a PunkConsole output on pin A1
punk_console_l = PunkConsole(board.A1)
punk_console_r = PunkConsole(board.D13)

# define the two potentiometer inputs
f_in = analogio.AnalogIn(board.A2)
pw_in = analogio.AnalogIn(board.A3)

while True:
    # read the inputs, map to practical audio ranges, send to PunkConsole instances
    punk_console_l.frequency = map_range(f_in.value, 0, 65535, 3, 3000)
    punk_console_l.pulse_width_ms = map_range(pw_in.value, 0, 65535, 0.5, 5.0)

    punk_console_r.frequency = map_range(f_in.value, 0, 65535, 3000, 3)
    punk_console_r.pulse_width_ms = map_range(pw_in.value, 0, 65535, 5.0, 0.5)
