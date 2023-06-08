import csv
import argparse
import numpy as np
from os.path import isfile
from scipy.io import wavfile

# TODO: this runs for one part at a time, should be able to loop through/parallel all files for a patient
def deid(sid, folder, file, day, part, verbose=False):

    # Input/output directories
    main_dir = '/Volumes/Epilepsy_ECOG/ecog/data/'
    sid_dir = main_dir + 'NY' + sid
    partname = 'NY' + sid + '_' + day + '_Part' + part
    audiofile = sid_dir + '/ZoomAudioFiles/' + folder + '/' + file + '.wav'
    outfile = sid_dir + '/DeidAudio/DeidAudio/' + partname + '_deid.wav'

    silences_fn = sid_dir + '/DeidAudio/DeidSpreadsheets/' + partname + '.csv'

    # Read raw audio file
    fs, audio = wavfile.read(audiofile) # signal = n_samples x n_channels
    signal = audio.copy()
    if verbose:
        print('Audio file:', signal.shape, fs)

    # Read silences file
    silences = []
    with open(silences_fn, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) == 0:
                continue

            # Zero-out audio according to silences file
            start_min, start_sec = float(row[0]), float(row[1])
            end_min, end_sec = float(row[2]), float(row[3])

            start = int((start_min*60 + start_sec) * fs)
            end = int((end_min*60 + end_sec) * fs)

            if start >= end:
                print('PROBLEM', start, end)

            if verbose:
                print('Silence ', start, end)

            silences.append(audio[start:end])
            signal[start:end] = 0.

    # Write deid audio file
    fn = outfile + '_deid.wav'
    wavfile.write(fn, fs, signal)

    # Check if silences are correct
    #silence_np = np.concatenate(silences)
    #fn = silences_fn[:pivot] + '_silences.wav'
    #wavfile.write(fn, fs, silence_np)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='De-id wav file with silences')
    parser.add_argument('sid', help='subject dir') 
    parser.add_argument('folder', help='in-subject folder')
    parser.add_argument('file', help='raw WAV file name') 
    parser.add_argument('day', help='day for output format')
    parser.add_argument('part', help='part for output format') 
    parser.add_argument('-v', action='store_true', default=False, help='Silence excel')
    args = parser.parse_args()

    # check if files actually exist/CHANGED HOW WE'RE ENTERING THE FILE NAME SO THIS WON'T WORK
    #if not isfile(args.wavfile):
    #    print('File does not exist: ' + args.wavfile)
    #    exit(1)

    #if not isfile(args.silencefile):
    #    print('File does not exist: ' + args.silencefile)
    #    exit(1)

    deid(args.sid, args.folder, args.file, args.day, args.part, args.v)
