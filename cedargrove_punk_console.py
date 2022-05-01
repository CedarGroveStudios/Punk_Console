## SPDX-FileCopyrightText: 2022 Cedar Grove Maker Studios
# SPDX-License-Identifier: MIT

"""
`cedargrove_punk_console` - CircuitPython-based Atari Punk Console.
=================================================
A CircuitPython-based Atari Punk Console emulation class object.
* Filename: cedargrove_punk_console.py v1.1
* Author(s): JG for Cedar Grove Maker Studios
"""
__repo__ = "https://github.com/CedarGroveStudios/Punk_Console"

import board
import pwmio


class PunkConsole:
    """A CircuitPython-based Atari Punk Console emulation class object based on
    the "Stepped Tone Generator" circuit, "Engineer's Mini-Notebook: 555
    Circuits", Forrest M. Mims III (1984).

    The CedarGrove Punk Console emulates an astable square-wave oscillator and
    synchronized non-retriggerable one-shot monostable multivibrator to create
    the classic stepped-tone generator sound of the Atari Punk Console. As with
    the original circuit, the oscillator frequency and one-shot pulse width are
    the input parameters. Once the Punk Console class is instantiated, the two
    input values are provided and the update() function is called to adjust the
    PWM parameters of the output pin to to create the output waveform.

    This version of the emulator works only with PWM-capable output pins.

    Depending on the timer and PWM capabilities of the host MPU board, the
    emulator can easily outperform the original analog circuit. Oscillator
    frequency is only limited by the MPU's PWM duty cycle and frequency
    parameters, which may create output signals well above the practical audio
    hearing range. Therefore, it is recommended that one-shot pulse width input
    be limited to the range of 0.5ms and 5ms and that the oscillator frequency
    input range be between 3Hz and 3kHz -- although experimentation is
    encouraged!

    The repo contains three examples, a simple single-channel console, an
    annoying stereo noisemaker, and a note table driven sequencer. For the first
    two examples, input is provided by potentiometers attached to
    two analog input pins. The sequencer is controlled by an internal list of
    notes that select the oscillator frequency; pulse width is potentiometer
    controlled.

    Minimim and maximum input ranges (may be further limited by the MPU):
    pulse_width: 0.05ms to  5000ms
    frequency:      1Hz to >4MHz

    Practical input ranges for audio (empirically determined):
    pulse_width:  0.5ms to 5ms
    frequency:      3Hz to 3kHz

    The CedarGrove Punk Console algorithm uses PWM frequency and duty cycle
    parameters to build the output waveform. The PWM output frequency is an
    integer multiple of the oscillator frequency input compared to the one-shot
    pulse width input:

        `pwm_freq = freq_in / (int((pulse_width) * freq_in) + 1)`

    The PWM output duty cycle is calculated after the PWM output frequency is
    determined. The PWM output duty cycle is the ratio of the one-shot pulse
    width and the wavelength of the PWM output frequency:

        `pwm_duty_cycle = pulse_width * pwm_freq`

    Notes:
    Future update: For non-PWM analog output, the plans are to use audiocore
    with a waveform sample in the `RawSample` binary array, similar to the
    `simpleio.tone()` helper. The output waveform's duty cycle will be adjusted
    by altering the contents of the array, perhaps with `ulab` to improve code
    execution time. The `audiocore.RawSample.sample_rate` frequency is expected
    to be directly proportional to the original algorithm's PWM frequency output
    value, calculated from the `sample_rate` divided by the length of the
    `audiocore.RawSample` array (number of samples).

    MIDI control: A version that uses USB and/or UART MIDI is in the queue. Note
    that the property `PunkConsole.mute` could be used for note-on and note-off.
    `note_in_example.py` shows how muting can be used for individual notes.

    CV control: A Eurorack version was discussed, it's just a bit lower on the
    to-do list, that's all."""

    def __init__(self, pin, frequency=1, pulse_width_ms=0, mute=True):
        """Intantiate and start the oscillator. Initial output is muted by
        default.

        :param ~board pin: The PWM-capable output pin.
        :param int frequency: The oscillator frequency setting in Hertz.
         Defaults to 1 Hertz to squelch output noise.
        :param int pulse_width_ms: The non-retriggerable one-shot monostable
         multivibrator delay (pulse_width) setting in milliseconds. Defaults to
         zero milliseconds to squelch output noise.
        :param bool mute: The output signal state. `True` to mute; `False` to
         unmute. Defaults to muted.
        """

        self._pin = pin
        self._mute = mute
        try:
            # Instantiate PWM output with some initial low-noise values
            self._pwm_out = pwmio.PWMOut(self._pin, variable_frequency=True)
            self._pwm_out.frequency = 1
            self._pwm_out.duty_cycle = 0x0000
        except ValueError:
            # The pin is not PWM capable
            print("Specified pin is not PWM capable.")

        # Set the maximum PWM frequency and duty cycle values (PWMOut limits)
        self._pwm_freq_range = (2**32) - 1  # 4,294,967,295Hz (32-bits)
        self._pwm_duty_cycle_range = (2**16) - 1  # 65,535 = 1.0 duty cycle (16-bits)

        # Limit the input frequency range; 1 Hz to PWM maximum frequency
        self._freq_in = min(max(frequency, 1), self._pwm_freq_range)

        # Limit the input pulse_width to an emperically-determined range: 50us to 5 seconds
        self._pulse_width_ms = min(max(pulse_width_ms, 0.050), 5000)

        # Set the PWM output frequency based on freq_in and pulse_width_ms
        self._pwm_freq = self._freq_in / (
            int((self._pulse_width_ms / 1000) * self._freq_in) + 1
        )
        self._pwm_out.frequency = int(round(self._pwm_freq, 0))

        # Set the PWM output duty cycle based on pulse_width_ms and pwm_freq
        self._pwm_duty_cycle = (self._pulse_width_ms / 1000) * self._pwm_freq
        if not self._mute:
            self._pwm_out.duty_cycle = int(
                self._pwm_duty_cycle * self._pwm_duty_cycle_range
            )
        else:
            self._pwm_out.duty_cycle = 0

    @property
    def frequency(self):
        return self._freq_in

    @frequency.setter
    def frequency(self, new_frequency):
        self._freq_in = min(max(new_frequency, 1), (2**32) - 1)
        self._lambda_in = 1 / self._freq_in
        self._update()

    @property
    def pulse_width_ms(self):
        return self._pulse_width_in

    @pulse_width_ms.setter
    def pulse_width_ms(self, new_width):
        self._pulse_width_ms = min(max(new_width, 0.050), 5)
        self._update()

    @property
    def mute(self):
        return self._mute

    @mute.setter
    def mute(self, new_mute):
        self._mute = new_mute
        self._update()

    def _update(self):
        """Recalculate and set PWM frequency and duty cycle using current
        frequency and pulse width input values."""

        # Set the PWM output frequency based on freq_in and pulse_width_ms
        self._pwm_freq = self._freq_in / (
            int((self._pulse_width_ms / 1000) * self._freq_in) + 1
        )
        self._pwm_out.frequency = int(round(self._pwm_freq, 0))

        # Set the PWM output duty cycle based on pulse_width_ms and pwm_freq
        self._pwm_duty_cycle = (self._pulse_width_ms / 1000) * self._pwm_freq
        if not self._mute:
            self._pwm_out.duty_cycle = int(
                self._pwm_duty_cycle * self._pwm_duty_cycle_range
            )
        else:
            self._pwm_out.duty_cycle = 0
