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
from adafruit_midi.timing_clock import TimingClock
# from adafruit_midi.channel_pressure        import ChannelPressure
from adafruit_midi.control_change import ControlChange
from adafruit_midi.note_off import NoteOff
from adafruit_midi.note_on import NoteOn
from adafruit_midi.pitch_bend import PitchBend

from cedargrove_unit_converter.music_MIDI import note_or_name, note_to_frequency
from cedargrove_punk_console import PunkConsole


# 0 is MIDI channel 1
midi = adafruit_midi.MIDI(midi_in=usb_midi.ports[0], in_channel=0)

print("Midi input test with pauses")

# Convert channel numbers at the presentation layer to the ones musicians use
print("Input channel:", midi.in_channel + 1)

# play with the pause to simulate code doing other stuff
# in the loop
pauses = [0] * 10 + [0.010] * 10 + [0.100] * 10 + [1.0] * 10

while True:
    for pause in pauses:
        msg = midi.receive()
        if msg is not None:
            print(time.monotonic(), msg)
        if pause:
            time.sleep(pause)



# note name, beats
notes = [
    ('C5', 1/2),
    ('E5', 1/4),
    ('G5', 1/4),
    ('C6', 1/2),
    ('B5', 1/4),
    ('G5', 1/4),
    ('F5', 1/4),
    ('D5', 1/4),
]

tempo = 120  # beats-per-minute
tempo_delay = 60 / tempo  # seconds-per-beat

# instantiate a PunkConsole output on pin A1 (PWM-capable)
punk_console_l = PunkConsole(board.A1, mute=True)

# define the potentiometer input for pulse-width
pw_in = analogio.AnalogIn(board.A3)  # One-Shot Pulse Width

uart = busio.UART(board.TX, board.RX, baudrate=31250, timeout=0.001)  # init UART
midi_in_channel = 2
midi_out_channel = 1
midi = adafruit_midi.MIDI(
    midi_in=uart,
    midi_out=uart,
    in_channel=(midi_in_channel - 1),
    out_channel=(midi_out_channel - 1),
    debug=False,
)

pixel = neopixel.NeoPixel(board.NEOPIXEL, 1)
pixel[0] = 0x020000

i = 0

while True:
    # read the inputs, map to practical audio ranges, send to PunkConsole instance
    #   oscillator frequency determined by note_or_name and note_to_frequency helpers
    #   one-shot pulse width range: 0.5ms to 5ms
    punk_console_l.mute = False

    if i >= len(notes):
        i = 0

    punk_console_l.frequency = note_to_frequency(note_or_name(notes[i][0]))
    punk_console_l.pulse_width_ms = map_range(pw_in.value, 0, 65535, 0.5, 5.0)
    punk_console_l.mute = False

    pixel[0] = 0x000200

    time.sleep(notes[i][1] * tempo_delay)
    print(i, notes[i][0], punk_console_l.frequency, notes[i][1])
    i += 1

    pixel[0] = 0x000000
