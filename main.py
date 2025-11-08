import math
import time
from PIL import Image
import winsound as sound

BEEP_DURATION = 30
FREQUENCY_OFFSET = 200
PAUSE_DURATION = 0.1
INPUT_FOLDER = 'images/'
FILE_NAME = 'test.png'

while True:
    scale_down_factor = 0.02

    img = Image.open(f"{INPUT_FOLDER}{FILE_NAME}")
    width, height = img.size

    img = img.resize((int(width * scale_down_factor), int(height * scale_down_factor)))
    width, height = img.size

    total_pixels_in_image = width * height

    img = img.convert("L")
    pixels = img.load()

    values = []

    for i in range(0, width):
        for j in range(0, height):
            values.append(pixels[i,j])

    transmission_total = total_pixels_in_image / 8
    transmission_minutes = int(math.floor(transmission_total / 60))
    transmission_seconds = transmission_total % 60

    print(height, width, total_pixels_in_image)
    print(f"WARNING! ESTIMATED TRANSMISSION TIME = {transmission_minutes}m {transmission_seconds}s")
    user_choice = input("Would you like to continue? (y/n): ").strip().lower()
    if user_choice == "n":
        break

    for i in range(0,3):
        print("COUNTDOWN: " + str(3-i))
        sound.Beep(500, 50)
        time.sleep(1)

    print("TRANSMITTING... (Press CTRL+C to stop the transmission)")

    for value in values:
        sound.Beep((value*7)+FREQUENCY_OFFSET, BEEP_DURATION)
        time.sleep(PAUSE_DURATION)

    print("\nFinished\n")
    break