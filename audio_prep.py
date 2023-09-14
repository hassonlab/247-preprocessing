"""Prepare audio data for transcription.

This is the third module to run in the 24/7 preprocessing pipeline. It must be run
after patient_prep.py and is strongly recommended to be run after ecog_prep.py. 
Removes silences from de-identified audio filess, slow audio by 5%, denoise audio.

Typical usage example:

    audio_prep.py --sid sub-001
"""

import pandas as pd
from utils import arg_parse
from subject import Subject, Audio

def crop_silence(subject_n,transcribe_audio):
    partname = str(transcribe_audio.name).split('_')
    silenceFile = ''.join([str(subject_n.silencePath),'/',partname[0],
                           '_',partname[1],'_silences.csv'])
    transcribe_audio.name = ''.join([str(subject_n.audioTranscribePath),'/',
                                     partname[0],'_',partname[1],'_transcribe.wav'])
    transcribe_audio.crop(silenceFile)
    return 

def main():

    args = arg_parse()
    sid = args.sid
    input_name = args.input_name

    subject_n = Subject(sid)
    subject_n.update_log('03_audio_prep: start')
    subject_n.audio_list()

    for file in subject_n.audDeid_files:
        transcribe_audio = Audio(sid,file)
        transcribe_audio.read_audio()
        crop_silence(subject_n,transcribe_audio)
        transcribe_audio.slow()
        #audio.denoise_audio(transcribe_audio)
        transcribe_audio.write_audio()

    subject_n.update_log('03_audio_prep: end')

    return

if __name__ == "__main__":
    main()