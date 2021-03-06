############################################################################
#																		   #
#			Musical Note Identification							   		   #
#																		   #
############################################################################

import numpy as np 
import wave
import struct

sampling_freq = 44100

# adjust appropriately
cutoff_amplitude = 0
note_frequencies = [ 1046.50,  1174.66,  1318.51,  1396.91,  1567.98,  1760.00,  1975.53]
note_frequencies.extend([2093.00,  2349.32,  2637.02,  2793.83,  3135.96,  3520.00,  3951.07])
note_frequencies.extend([ 4186.01,  4698.63,  5274.04,  5587.65,  6271.93,  7040.00,  7902.13])

note_values = {1046.50:'C6',  1174.66:'D6',  1318.51:'E6',  1396.91:'F6',  1567.98:'G6',  1760.00:'A6',  1975.53:'B6',
				2093.00:'C7',  2349.32:'D7',  2637.02:'E7',  2793.83:'F7',  3135.96:'G7',  3520.00:'A7',  3951.07:'B7',
				4186.01:'C8',  4698.63:'D8',  5274.04:'E8',  5587.65:'F8',  6271.93:'G8',  7040.00:'A8',  7902.13:'B8'}

#### reads a .wav file and converts it into an integer array of sound ####
def get_sound(sound_file):   
    file_length = sound_file.getnframes()
    sound = np.zeros(file_length)
    for i in range(file_length):
        data = sound_file.readframes(1)
        data = struct.unpack("<h", data)
        sound[i] = int(data[0])
    sound = np.divide(sound, float(2**15))
    return sound

#### returns the rms value of a particular window ####
def window_rms(a):
	window_length = len(a)
	square = np.power(a, 2)
	window = np.ones(window_length)/float(window_length)
	return np.sqrt(np.convolve(square, window, 'valid'))

#### Returns a list of windows in time-domain ####
def get_windows(sound, window_length):
	windows = []
	for i in range(int(len(sound)/window_length)):
		windows.append(sound[i*window_length:(i+1)*window_length])
	return windows

def get_rms_values(windows):
	values = []
	for window in windows:
		values.append(window_rms(window))
	return values

#### filters out the regions of silence ####
def filter_windows(windows, rms_values):
	for i in range(len(windows)):
		if rms_values[i] < cutoff_amplitude:
			windows[i] = np.zeros(len(windows[i]))
			rms_values[i] = 0

#### returns a list of continuous non-silent sounds (notes) ####
def get_notes_in_time_domain(windows, rms_values):
	j = 0;
	notes = []
	notes.append([])
	silent = False
	for i in range(len(windows)):
		if rms_values[i] > 0:
			silent = False
			notes[j].extend(windows[i])
		else:
			if not silent:
				j = j+1
				notes.append([])
				silent = True
	return notes

def notes_in_frequency(notes):
	note_freqs = []
	for note in notes:
		w = np.fft.fft(note)
		freqs = np.fft.fftfreq(len(w))
		freq = freqs[np.argmax(np.abs(w))]
		note_freqs.append(abs(freq*sampling_freq))
	return note_freqs


#### matches frequency with a note ####
def match_frequency_to_note(frequency):
	freq = min(note_frequencies, key=lambda x:abs(x-frequency))
	index = note_frequencies.index(freq)
	return note_values[note_frequencies[index]]

#### finds the corresponding note according to peak frequency ####
def get_notes_from_frequencies(freq_notes):
	actual_notes = []
	for note in freq_notes:
		actual_notes.append(match_frequency_to_note(note))
	return actual_notes

def play(sound_file):

    sound = get_sound(sound_file)

    window_length = int(0.01* sampling_freq)
    windows = get_windows(sound, window_length)
    rms_values = get_rms_values(windows)
    filter_windows(windows, rms_values)
    time_notes = get_notes_in_time_domain(windows, rms_values)
    time_notes.pop()
    freq_notes = notes_in_frequency(time_notes)
    identified_notes = get_notes_from_frequencies(freq_notes)
    return identified_notes

############################## Read Audio File #############################

if __name__ == "__main__":
    #code for checking output for single audio file
    sound_file = wave.open('Test_Audio_files/Audio_1.wav', 'r')
    Identified_Notes = play(sound_file)
    print("Notes = ", Identified_Notes)

    # code for checking output for all images
    Identified_Notes_list = []
    for file_number in range(1,6):
        file_name = "Test_Audio_files/Audio_"+str(file_number)+".wav"
        sound_file = wave.open(file_name)
        Identified_Notes = play(sound_file)
        Identified_Notes_list.extend(Identified_Notes)
    print (Identified_Notes_list)
