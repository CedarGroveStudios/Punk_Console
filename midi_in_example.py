## SPDX-FileCopyrightText: 2022 Cedar Grove Maker Studios
# SPDX-License-Identifier: MIT

# cedargrove_punk_console.midi_in_example.py v1.0

# Tested on an RP2040 Feather using CircuitPython v7.1.1
# Waveform Output pin: A1 (PWM digital output, not analog DAC output)
# Oscillator Frequency Input pin: A2 (analog input)
# One-Shot Multivibrator Pulse Width Input pin: A3 (analog input)

import time
import board
import busio
import analogio
import pwmio
import neopixel
from simpleio import map_range

import usb_midi
import adafruit_midi
#from adafruit_midi.timing_clock import TimingClock

from adafruit_midi.channel_pressure        import ChannelPressure
from adafruit_midi.control_change import ControlChange
from adafruit_midi.note_off import NoteOff
from adafruit_midi.note_on import NoteOn
from adafruit_midi.pitch_bend import PitchBend

from cedargrove_unit_converter.music_MIDI import note_or_name, note_to_frequency
from cedargrove_punk_console import PunkConsole

# instantiate the neopixel status indicator
pixel = neopixel.NeoPixel(board.NEOPIXEL, 1)
pixel[0] = 0x020000

# instantiate a PunkConsole output on pin A1 (PWM-capable)
punk_console_l = PunkConsole(board.A1, mute=True)

# 0 is MIDI channel 1
uart = busio.UART(board.TX, board.RX, baudrate=31250, timeout=0.001)  # init UART
midi = adafruit_midi.MIDI(midi_in=uart, in_channel=0)

print("Midi input test with pauses")
pixel[0] = 0x020000

# Convert channel numbers at the presentation layer to the ones musicians use
print("Input channel:", midi.in_channel + 1)

pixel[0] = 0x000200
note = None
pressure = 0
note_status = "off"
control = 0

while True:
    msg = midi.receive()
    if msg is not None:
        if pixel[0] == (0, 2, 0):
            pixel[0] = 0x020200
        else:
            pixel[0] = 0x000200
        #print(f"time: {time.monotonic():6.3f}  msg: {msg}")
        if isinstance(msg, NoteOn):
            # 7-bit values
            #print(f"note: {msg.note}  velocity: {msg.velocity}")
            note = msg.note
            note_status = "on"
        if isinstance(msg, NoteOff):
            # 7-bit values
            #print(f"note: {msg.note}  velocity: {msg.velocity}")
            note = msg.note
            note_status = "off"
        if isinstance(msg, ChannelPressure):
            pass
            # 7-bit value
            #print(f"pressure: {msg.pressure}")
            pressure = msg.pressure
        if isinstance(msg, PitchBend):
            pass
            # 14-bit value, 8192 is center pitch
            #print(f"pitch_bend: {msg.pitch_bend}")
        if isinstance(msg, ControlChange):
            # 7-bit value
            #print(f"control: {msg.control}  value: {msg.value}")
            control = msg.value

    if note is not None:
        punk_console_l.frequency = note_to_frequency(note)
        punk_console_l.pulse_width_ms = map_range(control, 0, 127, 0.5, 5.0)
    if note_status == "on":
        punk_console_l.mute = False
    else:
        punk_console_l.mute = True
