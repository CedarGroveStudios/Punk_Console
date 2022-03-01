# CedarGroveStudios Punk_Console


A CircuitPython-based Atari Punk Console emulator class object based on the "Stepped Tone Generator" circuit, "Engineer's Mini-Notebook: 555 Circuits", Forrest M. Mims III (1984).

The CedarGrove Punk Console emulates an astable square-wave oscillator and synchronized non-retriggerable one-shot monostable multivibrator to create the classic stepped-tone generator sound of the Atari Punk Console. As with the original circuit, the oscillator frequency and one-shot pulse width are the input parameters. Once the Punk Console class is instantiated, the two input values are provided and the `update()` function is called to adjust the PWM parameters of the output pin to to create the output waveform.

Depending on the timer and PWM capabilities of the host MPU board, the emulator can easily outperform the original analog circuit. Oscillator frequency is only limited by the MPU's PWM duty cycle and frequency parameters, which may create output signals well above the practical audio hearing range. Therefore, it is recommended that one-shot pulse width input be limited to the range of 0.5ms and 5ms and that the oscillator frequency input range be between 3Hz and 3kHz -- although experimentation is encouraged!

The repo contains two examples, a simple single-channel console and an annoying stereo noisemaker. Input is provided by potentiometers attached to two analog input pins.

The current version of the emulator works only with PWM-capable output pins. An analog output (DAC) waveform version is in the works.


    Minimim and maximum input ranges (may be further limited by the MPU):
    pulse_width: 0.05ms to  5000ms
    frequency:      1Hz to >4MHz

    Practical input ranges for audio (empirically determined):
    pulse_width:  0.5ms to 5ms
    frequency:      3Hz to 3kHz


The Punk Console algorithm uses PWM frequency and duty cycle parameters to build the output waveform. The PWM output frequency is an integer multiple of the oscillator frequency input compared to the one-shot pulse width input:

        pwm_freq = freq_in / (int((pulse_width) * freq_in) + 1)


The PWM output duty cycle is calculated after the PWM output frequency is determined. The PWM output duty cycle is the ratio of the one-shot pulse width and the wavelength of the PWM output frequency:

        pwm_duty_cycle = pulse_width * pwm_freq


Notes:
- Future update: For non-PWM analog output, the plans are to use `audiocore` with a waveform sample in the `RawSample` binary array, similar to the `simpleio.tone()` helper. The output waveform's duty cycle will be adjusted by altering the contents of the array, perhaps with `ulab` to improve code execution time. The `audiocore.RawSample.sample_rate` frequency is expected to be directly proportional to the original algorithm's PWM frequency output value, calculated from the `sample_rate` divided by the length of the `audiocore.RawSample` array (number of samples).

- MIDI control: A version that uses USB and/or UART MIDI is in the queue.

- CV control: A Eurorack version was discussed, it's just a bit lower on the to-do list, that's all.

![Original Step Tone Generator Diagram](https://github.com/CedarGroveStudios/Punk_Console/blob/main/docs/CG_PunkConsole_04.jpeg)

![Oscillator Triggers One-Shot](https://github.com/CedarGroveStudios/Punk_Console/blob/main/docs/CG_PunkConsole_01.jpeg)

![Pulse Width Input Decreases](https://github.com/CedarGroveStudios/Punk_Console/blob/main/docs/CG_PunkConsole_02.jpeg)

![Oscillator Frequency Input Decreases](https://github.com/CedarGroveStudios/Punk_Console/blob/main/docs/CG_PunkConsole_03.jpeg)
