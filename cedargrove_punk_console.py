## SPDX-FileCopyrightText: 2022 Cedar Grove Maker Studios
# SPDX-License-Identifier: MIT

"""
`cedargrove_punk_console` - CircuitPython-based Atari Punk Console.
=================================================
cedargrove_punk_console.py v1.0

A CircuitPython-based Atari Punk Console emulation class object.

* Author(s): JG for Cedar Grove Maker Studios
"""
__repo__ = "https://github.com/CedarGroveStudios/Punk_Console"

import board
import pwmio

class PunkConsole:
    """ A CircuitPython-based Atari Punk Console emulation class object based
    on the "Stepped Tone Generator" circuit, "Engineer's Mini-Notebook: 555
    Circuits", Forrest M. Mims III (1984).

    Input ranges:
    pulse_width: 50us to  5sec (2kHz to  2Hz; may be limited by the MPU)
    frequency:    1Hz to >4MHz (may be limited by the MPU)

    Practical input ranges for audio (emperically determined):
    pulse_width: 0.5ms to 5ms
    frequency: 3Hz to 3kHz

    PWM output ranges:
    pwm frequency:  0 to 2**32 -1  (32-bits)
    pwm duty_cycle: 0 to 2**16 -1  (16-bits)

    The CedarGrove Punk Console algorithm uses PWM frequency and duty cycle
    parameters to build the output waveform. The PWM output frequency is an
    integer multiple of the input frequency depending on the input pulse width:

        pwm_freq = freq_in / (int((pulse_width) * freq_in) + 1)

    The PWM output duty cycle is calculated after the PWM output frequency is
    determined. The PWM output duty cycle is the ratio of the input pulse width
    and the wavelength of the PWM output frequency:

        pwm_duty_cycle = pulse_width * pwm_freq

    Notes:
    Future update: For non-PWM analog pins, use audiocore with a waveform sample
    in the RawSample binary array, similar to the simpleio.tone() helper. Adjust
    the output waveform's duty cycle by altering the contents of the array,
    perhaps with ulab to improve code execution time. The
    audiocore.RawSample.sample_rate frequency will be proportional to the
    original algorithm's PWM frequency output value, likely calculated from the
    sample_rate divided by the length of the audiocore.RawSample array (number
    of samples).  """

    def __init__(self, pin, frequency=1, pulse_width_ms=0):
        self._pin = pin
        try:
            # Instantiate PWM output with some initial low-noise values
            self._pwm_out=pwmio.PWMOut(self._pin, variable_frequency=True)
            self._pwm_out.frequency = 1
            self._pwm_out.duty_cycle = 0x0000
        except ValueError:
            # The pin is not PWM capable
            print("Specified pin is not PWM capable.")

        # Set the maximum PWM frequency and duty cycle values (PWMOut limits)
        self._pwm_freq_range = (2 ** 32) - 1  # 4,294,967,295Hz (32-bits)
        self._pwm_duty_cycle_range = (2 ** 16) - 1  # 65,535 = 1.0 duty cycle (16-bits)

        # Limit the input frequency range; 1 Hz to PWM maximum frequency
        self._freq_in = min(max(frequency, 1), self._pwm_freq_range)

        # Limit the input pulse_width to an emperically-determined range: 50us to 5 seconds
        self._pulse_width_ms = min(max(pulse_width_ms, 0.050), 5000)

        # Determine the PWM output frequency based on freq_in and pulse_width_ms
        self._pwm_freq = self._freq_in / (int((self._pulse_width_ms / 1000) * self._freq_in) + 1)
        self._pwm_out.frequency = int(round(self._pwm_freq, 0))

        # Determine the PWM output duty cycle based on pulse_width_ms and pwm_freq
        self._pwm_duty_cycle = (self._pulse_width_ms / 1000) * self._pwm_freq
        self._pwm_out.duty_cycle = int(self._pwm_duty_cycle * self._pwm_duty_cycle_range)

        return

    @property
    def frequency(self):
        return self._freq_in

    @frequency.setter
    def frequency(self, value):
        self._freq_in = min(max(value, 1), (2 ** 32) - 1)
        self._lambda_in = 1 / self._freq_in
        self.update()

    @property
    def pulse_width_ms(self):
        return self._pulse_width_in

    @pulse_width_ms.setter
    def pulse_width_ms(self, value):
        self._pulse_width_ms = min(max(value, 0.050), 5)
        self.update()


    def update(self):
        """Recalculate and set PWM frequency and duty cycle using current
        frequency and pulse width input values."""

        # Determine the PWM output frequency based on freq_in and pulse_width_ms
        self._pwm_freq = self._freq_in / (int((self._pulse_width_ms / 1000) * self._freq_in) + 1)
        self._pwm_out.frequency = int(round(self._pwm_freq, 0))

        # Determine the PWM output duty cycle based on pulse_width_ms and pwm_freq
        self._pwm_duty_cycle = (self._pulse_width_ms / 1000) * self._pwm_freq
        self._pwm_out.duty_cycle = int(self._pwm_duty_cycle * self._pwm_duty_cycle_range)

        return
