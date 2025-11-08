import numpy as np
import simpleaudio as sa
import time

sample_rate = 44100
duration = 0.3  # seconds
frequency = 440  # A4

t = np.linspace(0, duration, int(sample_rate * duration), False)
waveform = np.sin(2 * np.pi * frequency * t)
waveform *= 32767 / np.max(np.abs(waveform))
waveform = waveform.astype(np.int16)

play_obj = sa.play_buffer(waveform, 1, 2, sample_rate)
play_obj.wait_done()
time.sleep(0.5)

play_obj2 = sa.play_buffer(waveform, 1, 2, sample_rate)
play_obj2.wait_done()
