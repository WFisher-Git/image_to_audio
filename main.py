import math
import time
from PIL import Image
import winsound as sound
import sys
import numpy as np
import sounddevice as sd
import soundfile as sf

BEEP_DURATION = 30
FREQUENCY_OFFSET = 1275
PAUSE_DURATION = 0.1
INPUT_FOLDER = 'images/'
FILE_NAME = 'test.png'
SAMPLE_RATE = 44100

def load_file():
    scale_down_factor = 0.02

    img = Image.open(f"{INPUT_FOLDER}{FILE_NAME}")
    width, height = img.size

    img = img.resize((int(width * scale_down_factor), int(height * scale_down_factor)))

    img = img.convert("L")

    return img


def transmit(img):

    pixels = img.load()

    width, height = img.size
    total_pixels_in_image = width * height

    values = []
    for i in range(0, width):
        for j in range(0, height):
            values.append(pixels[i,j])

    transmission_total = total_pixels_in_image / 8
    transmission_minutes = int(math.floor(transmission_total / 60))
    transmission_seconds = transmission_total % 60

    print(f"WARNING! ESTIMATED TRANSMISSION TIME = {transmission_minutes}m {transmission_seconds}s")
    user_choice = input("Would you like to continue? (y/n): ").strip().lower()
    if user_choice == "n":
        sys.exit()

    for i in range(0,3):
        print("COUNTDOWN: " + str(3-i))
        sound.Beep(500, 50)
        time.sleep(1)

    print("TRANSMITTING... (Press CTRL+C to stop the transmission)")

    for i in range(0, len(values)):
        values[i] = (values[i]*5) + 200
    
    combined = []
    for i in range(0, len(values), 3):
        tone1 = values[i]
        if i+1 < len(values): tone2 = values[i+1] + FREQUENCY_OFFSET
        if i+2 < len(values): tone3 = values[i+2] + (2 * FREQUENCY_OFFSET)

        for data in play_tones([tone1, tone2, tone3]):
            combined.append(data)

    sf.write('audio/test.wav', combined, SAMPLE_RATE)
    

def play_tones(frequencies, duration=0.3, volume=50):

    time = np.linspace(0, duration, int(SAMPLE_RATE * duration), endpoint=False)
    
    # Generate each sine wave and sum them
    waves = []
    for frequency in frequencies:
        waves.append(np.sin(2 * np.pi * frequency * time))

    combined = []
    for i in range(0, len(time)):
        combined.append(waves[0][i] + waves[1][i] + waves[2][i])
    
    # Limit the amplitude to between -1 and 1 (for the speaker)
    combined = combined / max(np.abs(combined))
    
    combined *= (volume/100)

    sd.play(combined, SAMPLE_RATE)
    sd.wait()

    return combined


transmit(load_file())
