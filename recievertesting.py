from matplotlib import pyplot as plt
import numpy as np
from scipy.io import wavfile
from PIL import Image

#VARIABLES
input_folder = 'audio/'
file_name = 'audio1audacity.wav'
output_folder = 'outputs/'
output_name = 'audio1audacity.png'
height, width = 20, 30
total_pixels_in_image = int(width * height)

def plot(x, y, xlabel, ylabel, title, limit):
    plt.plot(x, y)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    if limit != -1:
        plt.xlim(0, limit)
    plt.show()

def get_beep_frequency(data, sample_rate, start, end):
    segment = data[start:end]  # Left channel
    segment_length = end - start           

    # FFT and PSD
    fhat = np.fft.fft(segment, segment_length)
    PSD = fhat * np.conj(fhat) / segment_length
    freq = np.fft.fftfreq(segment_length, d=1/sample_rate)[:segment_length//2]
    PSD = PSD[:segment_length//2]

    # Limit to frequencies under 2550 Hz
    mask = freq < 2550
    freq_limited = freq[mask]
    PSD_limited = PSD[mask]

    beep_frequency = freq_limited[np.argmax(PSD_limited)]

    #plot(freq_limited, PSD_limited.real, "hz", "power", f"PSD of Samples {start}-{end}", 2550)

    return beep_frequency

def load_file():
    sample_rate, data = wavfile.read(f"{input_folder}{file_name}")
    data = np.int16(data)
    total_samples = len(data)
    length = total_samples / sample_rate
    #set up time axis
    time = np.linspace(0., length, total_samples)

    return (data, sample_rate, total_samples, length, time)

def get_beep_times(data, time, threshold):
    data_binary = np.where(data < threshold, 0, 10000) 

    all_beep_times = time[data_binary == 10000]

    reduced_beep_times = []
    start_of_beep = all_beep_times[0]

    for i in range(len(all_beep_times) - 1):
        if all_beep_times[i + 1] >= all_beep_times[i] + 0.075:
            end_of_beep = all_beep_times[i]
            reduced_beep_times.append((start_of_beep + end_of_beep) / 2)
            start_of_beep = all_beep_times[i + 1]

    end_of_beep = all_beep_times[-1]
    reduced_beep_times.append((start_of_beep + end_of_beep) / 2)   

    return reduced_beep_times

def generate_image(pixels):
    #reshape the pixels to match the transmitted image, generate the image and save
    img = pixels.reshape(height, width)

    img = Image.fromarray(img)

    img = img.transpose(Image.Transpose.ROTATE_270)
    img = img.transpose(Image.Transpose.FLIP_LEFT_RIGHT)

    img.save(f"{output_folder}{output_name}")

def get_threshold():
    image_qualities = []

    for i in range(0, 600, 10):
        threshold = i
        data, sample_rate, _, _, time = load_file()

        selected_samples = []
        for t in get_beep_times(data, time, threshold):
            start_sample = int((t - 0.03) * sample_rate)
            end_sample = int((t + 0.03) * sample_rate)
            selected_samples.append([start_sample, end_sample])

        pixels = []
        for start, end in selected_samples:
            value = np.int16(get_beep_frequency(data, sample_rate, start, end)) 
            value = (value-200)/7                          
            if value >= 0:                                  
                pixels.append(value)

        image_qualities.append(len(pixels))
    
    return image_qualities.index(max(image_qualities))

def main():

    #gather generated variables
    data, sample_rate, total_samples, length, time = load_file()

    print("FILE DETAILS\n------------\n")
    print(f"Sample rate = {sample_rate}")
    print(f"Data length = {total_samples}")
    print(f"Seconds = {length}\n")

    print("Analyzing wav file...")
    threshold = get_threshold() * 10
    print(f"Threshold: {threshold}")
    print("Generating image...")

    #plot(time, data, "s", "amplitude", "raw data", -1)

    #plot(time, data_binary, "s", "amplitude", "binary data", -1)

    #isolate the samples within the area 0.03 seconds around the beep
    selected_samples = []
    for t in get_beep_times(data, time, threshold):
        start_sample = int((t - 0.03) * sample_rate)
        end_sample = int((t + 0.03) * sample_rate)
        selected_samples.append([start_sample, end_sample])

    pixels = []
    for start, end in selected_samples:
        #run a fast fourier transform on the beep to get the frequency
        value = np.int16(get_beep_frequency(data, sample_rate, start, end)) 
        #decode the frequency into a pixel value
        value = (value-200)/7   
        #check if it is valid before adding it to the pixels array                         
        if value >= 0:                                  
            pixels.append(value)

    print(len(pixels))

    #pad the image with black pixels if not all data has been transferred
    for i in range(0, total_pixels_in_image):
        pixels.append(0)
    pixels = (np.uint8(pixels))[:total_pixels_in_image]

    generate_image(pixels)


if __name__ == "__main__":
    main()