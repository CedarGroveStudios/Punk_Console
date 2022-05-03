# CedarGroveStudios Punk_Console

![Punk Console Stereo Test](https://github.com/CedarGroveStudios/Punk_Console/blob/main/docs/Stereo_Punk_Console_test.png)

A CircuitPython-based Atari Punk Console emulator class object based on the "Stepped Tone Generator" circuit, "Engineer's Mini-Notebook: 555 Circuits", Forrest M. Mims III (1984).

The CedarGrove Punk Console emulates an astable square-wave oscillator and synchronized non-retriggerable one-shot monostable multivibrator to create the classic stepped-tone generator sound of the Atari Punk Console. As with the original circuit, the oscillator frequency and one-shot pulse width are the input parameters. Instantiation of the Punk Console class will start the output waveform based on the input parameters and enable the output signal if `mute=False`. If no input parameters are provided, the output signal will be disabled regardless of the mute value. Once instantiated, the class is controlled by the `frequency`, `pulse_width_ms`, and `mute` properties.

This version of the emulator works only with PWM-capable output pins.

Depending on the timer and PWM capabilities of the host MPU board, the emulator can easily outperform the original analog circuit. Oscillator frequency is only limited by the MPU's PWM duty cycle and frequency parameters, which may create output signals well above the practical audio hearing range. Therefore, it is recommended that one-shot pulse width input be limited to the range of 0.5ms and 5ms and that the oscillator frequency input range be between 3Hz and 3kHz -- although experimentation is encouraged!

The repo contains three examples, a simple single-channel console, an annoying stereo noisemaker, and a note table driven sequencer. For the first two examples, input is provided by potentiometers attached to two analog input pins. The sequencer is controlled by an internal list of notes that select the oscillator frequency; pulse width is potentiometer controlled.


    Typical minimim and maximum input ranges (subject to MPU limitations):
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

- MIDI control: A version that uses USB and/or UART MIDI is in the queue. Note that the `PunkConsole.mute` property could be used for note-on and note-off. `note_in_example.py` shows how muting can be used for individual notes.

- CV control: A Eurorack version was discussed, it's just a bit lower on the to-do list, that's all.

![Original Step Tone Generator Diagram](https://github.com/CedarGroveStudios/Punk_Console/blob/main/docs/CG_PunkConsole_04.jpeg)

![Oscillator Triggers One-Shot](https://github.com/CedarGroveStudios/Punk_Console/blob/main/docs/CG_PunkConsole_01.jpeg)

![Pulse Width Input Decreases](https://github.com/CedarGroveStudios/Punk_Console/blob/main/docs/CG_PunkConsole_02.jpeg)

![Oscillator Frequency Input Decreases](https://github.com/CedarGroveStudios/Punk_Console/blob/main/docs/CG_PunkConsole_03.jpeg)
