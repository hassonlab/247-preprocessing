"""Prepare audio data for transcription.

This is the third module to run in the 24/7 preprocessing pipeline. It must be run
after patient_prep.py and is strongly recommended to be run after ecog_prep.py. 
Removes silences from de-identified audio filess, slow audio by 5%, denoise audio.

Typical usage example:

    audio_prep.py --sid sub-001
"""

from utils import arg_parse
from subject import Subject
from audio import Audio
from silence import Silence
from config import Config


def crop_silence(subject_n: Subject, transcribe_audio: Audio):
    partname = str(transcribe_audio.name.name).split("_")
    part = partname[1][-3:]
    # TODO: change this
    silence_fname = subject_n.rename_files(
        subject_n.filenames["silence"].parent, "file", part, "silence"
    )
    transcribe_audio.file = subject_n.filenames[
        "audio_transcribe"
    ].parent / subject_n.rename_files(
        subject_n.filenames["audio_transcribe"].parent, "file", part, "audio_transcribe"
    )

    silence_file = Silence(subject_n.filenames["silence"].parent / silence_fname)
    silence_file.read_silence()
    silence_file.calc_silence()

    transcribe_audio.crop_audio(silence_file)
    return


def main():
    args = arg_parse()
    sid = args.sid
    input_name = args.input_name

    config = Config(sid)
    config.configure_paths()

    subject_n = Subject(sid)
    subject_n.filenames = config.filenames
    subject_n.update_log("03_audio_prep: start")
    subject_n.audio_list()

    for file in subject_n.audio_deid_files:
        transcribe_audio = Audio(file)
        transcribe_audio.in_path = subject_n.filenames["audio_downsampled"].parent
        transcribe_audio.read_audio()
        crop_silence(subject_n, transcribe_audio)
        transcribe_audio.slow_audio()
        # audio.denoise_audio(transcribe_audio)
        transcribe_audio.write_audio()

    subject_n.update_log("03_audio_prep: end")

    return


if __name__ == "__main__":
    main()
