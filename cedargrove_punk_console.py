# SPDX-FileCopyrightText: 2022 Cedar Grove Maker Studios
#
# SPDX-License-Identifier: MIT

"""
`cedargrove_punk_console` - Simple, beginner friendly IO.
=================================================

A CircuitPython-based Atari Punk Console emulation class object.

* Author(s): JG for Cedar Grove Maker Studios
"""
import time
import sys
import array  # use ulab instead?
import digitalio
import pwmio


try:
    # RawSample was moved in CircuitPython 5.x.
    if sys.implementation.version[0] >= 5:
        import audiocore
    else:
        import audioio as audiocore
    # Some boards have AudioOut (true DAC), others have PWMAudioOut.
    try:
        from audioio import AudioOut
    except ImportError:
        from audiopwmio import PWMAudioOut as AudioOut
except ImportError:
    pass  # not always supported by every board!


__version__ = "3.0.2"
__repo__ = "https://github.com/CedarGroveStudios/Punk_Console"


def tone(pin, frequency, duration=1, length=100):
    """
    Generates a square wave of the specified frequency on a pin

    :param ~microcontroller.Pin pin: Pin on which to output the tone
    :param float frequency: Frequency of tone in Hz
    :param int length: Variable size buffer (optional)
    :param int duration: Duration of tone in seconds (optional)
    """
    if length * frequency > 350000:
        length = 350000 // frequency
    try:
        # pin with PWM
        # pylint: disable=no-member
        with pwmio.PWMOut(
            pin, frequency=int(frequency), variable_frequency=False
        ) as pwm:
            pwm.duty_cycle = 0x8000
            time.sleep(duration)
        # pylint: enable=no-member
    except ValueError:
        # pin without PWM
        sample_length = length
        square_wave = array.array("H", [0] * sample_length)
        for i in range(sample_length / 2):
            square_wave[i] = 0xFFFF
        square_wave_sample = audiocore.RawSample(square_wave)
        square_wave_sample.sample_rate = int(len(square_wave) * frequency)
        with AudioOut(pin) as dac:
            if not dac.playing:
                dac.play(square_wave_sample, loop=True)
                time.sleep(duration)
            dac.stop()

def map_range(x, in_min, in_max, out_min, out_max):
    """
    Maps a value from one range to another.

    :return: Returns value mapped to new range
    :rtype: float
    """
    in_range = in_max - in_min
    in_delta = x - in_min
    if in_range != 0:
        mapped = in_delta / in_range
    elif in_delta != 0:
        mapped = in_delta
    else:
        mapped = 0.5
    mapped *= out_max - out_min
    mapped += out_min
    if out_min <= out_max:
        return max(min(mapped, out_max), out_min)
    return min(max(mapped, out_max), out_min)

class Punk_Console:
    def __init__(self, pin, frequency, pulse_width):
        self._pin = pin
        self._freq_in = min(max(frequency, 20), 20000)
        self._pulse_width_in = min(max(pulse_width, 0.00005), 0.050)

        self._lambda_freq_in = 1 / self._freq_input

        """
        Input ranges:
        pulse_width: 500us  to 500ms (2kHz to  2Hz)
        frequency:    20kHz to  20Hz (50us to 50ms)

        This version of the algorithm uses PWM to build the output waveform.
        The PWM frequency will shift as to provide the granularity needed to
        represent both the pulse width input value (_pulse_width_in) and the frequency input
        wavelength (_lambda_f_in):
            _pulse_width_freq = 1 / (_pulse_width_in + _lambda_freq_in)

        The PWM duty cycle establishes the relationship between the pulse width
        input (_pulse_width_in) and the PWM frequency (_pwm_freq):
            _duty_cycle = _pulse_width_in * _pwm_freq

        Step 1 (initialize):
            Set the PWM frequency based upon the input values.
        Step 2 (initialize):
            Set the PWM duty cycle based upon the PWM frequency and pulse width
            input values.
        Step 3 (update):
            Adjust the PWM duty cycle when the pulse width input changes.
            Test for boundaries:
                If the inactive portion of the output waveform becomes larger
                than the wavelength of the frequency input, adjust the PWM
                clock upwards (using _pwm_freq_step) until the inactive portion
                is smaller than or equal to the wavelength of the frequency
                input.
                If the inactive portion equals zero, adjust the PWM clock
                downwards until the inactive portion is no longer zero.

        Notes:
        If the specified pin is non-PWM, then adjust the duty cycle with the
        contents of the audiocore.RawSample binary array. The
        audiocore.RawSample.sample_rate frequency will be proportional to the
        PWM frequency value, likely the sample_rate divided by the length of the
        audiocore.RawSample array (number of samples). Consider using ulab for
        the array if changes become execution time constrained.

        """
