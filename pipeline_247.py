import time
import logging
import pandas as pd
from autologging import TRACE
from string import Template, Formatter
from classes.subject import Subject
from classes.config import Config
from classes.ecog import Ecog
from classes.audio import Audio
from classes.silence import Silence
from classes.transcript import Transcript

def get_silence_times(subject_n, file):

    silence_file = subject_n.rename_files(file, "silence")
    silence_times = Silence(silence_file)
    silence_times.read_silence()
    silence_times.calc_silence()

    return silence_times


def subject_prep(subject_n: Subject):
    """Set-up for processing new subject"""

    # Create parent directory for subject
    subject_n.create_dir()

    # Transfer files
    subject_n.transfer_files()

    # Adjust file names for consistency
    for filetype in [
        subject_n.edf_files,
        subject_n.audio_512_files,
        subject_n.audio_deid_files,
    ]:
        # TODO: IMPORTANT: Additional checks to make sure order is correct when sorting
        subject_n.rename_files(sorted(filetype), rename=True)

    # Create subject-level transcript to append to
    subject_n.create_subject_transcript()

    # NOTE: We can get the correct naming when we run downsampling/deid on nyu server


def ecog_prep(subject_n: Subject):
    """Split and process ECoG signal"""

    for file in subject_n.edf_files:
        ecog_file = Ecog(subject_n.sid, file)

        ecog_file.read_EDFHeader()
        ecog_file.end_datetime()
        ecog_file.read_channels(10, 10000)

        # TODO: Figure out how we're splitting files
        ecog_file.process_ecog()
        ecog_file.name = subject_n.rename_files(ecog_file.name, "ecog-processed")
        ecog_file.write_edf()


def audio_prep(subject_n: Subject):
    """Prepare audio file for transcription"""

    for file in subject_n.audio_deid_files:
        transcribe_audio = Audio(subject_n.sid, file)

        silence_times = get_silence_times(subject_n, file)
    
        transcribe_audio.read_audio()

        transcribe_audio.crop_audio(silence_times)
        transcribe_audio.slow_audio()
        # audio.denoise_audio(transcribe_audio)
        transcribe_audio.out_name = subject_n.rename_files(transcribe_audio.name, "audio-transcribe")
        transcribe_audio.write_audio()


def transcript_prep(subject_n: Subject, silence_times: Silence):
    """Prepare subject-level transcript"""

    for file in subject_n.audio_deid_files:
        transcript_filename = subject_n.rename_files(file, "transcript")
        # TODO: decide what to do about possible file mismatches (if we have an audio file but no transcript, etc.)
        if transcript_filename.is_file():
            transcript_file = Transcript(subject_n.sid, transcript_filename)

            if "silence_times" not in locals():
                 silence_times = get_silence_times(subject_n, file)

            transcript_prep(transcript_file, silence_times)

        subject_n.transcript = pd.concat(
            [subject_n.transcript, transcript_file.transcript]
        )
        
        transcript_file.parse_xml()
        transcript_file.convert_timedelta()
        transcript_file.compress_transcript(0.05)

        onset_day, onset_time = transcript_file.get_audio_info_csv()
        transcript_file.add_dt(onset_day, onset_time)

        transcript_file.agg_silences(silence_times)
    
    # Write subject-level transcript
    subject_n.transcript = (
        subject_n.transcript.rename_axis("part_idx")
        .sort_values(by=["onset", "part_idx"])
        .reset_index()
    )

    subject_n.transcript.to_csv(
        subject_n.filenames["transcript"].parents[1]
        / "_".join([subject_n.sid, "transcript.csv"])
    )


def main():
    # Get arguments
    args = Config.arg_parse()
    sid = args.sid
    steps = args.steps

    # Create config
    config = Config(sid)
    config.configure_paths_old()
    config.configure_paths_nyu()

    # Generate instance of subject class
    subject_n = Subject(sid, create_config=True)
    subject_n.filenames = config.filenames
    subject_n.__dict__.update(config.nyu_paths.items())

    # Get list of files to loop over for processing
    subject_n.audio_list()
    subject_n.edf_list()
    subject_n.silence_list()

    fun_list = [subject_prep, ecog_prep, audio_prep, transcript_prep]

    for fun in fun_list:
        if fun.__name__ in steps:
            print(fun.__name__ )
            fun(subject_n)

    breakpoint()

    logging.basicConfig(
        level=TRACE,
        filename=(config.filenames["log"] / "sub.log"),
        format="%(asctime)s %(levelname)s:%(name)s:%(funcName)s:%(message)s",
    )

    config.write_config_old()

    # TODO: move this to end
    # if not (subject_n.basePath / sid + '-summary.json').exists(): subject_n.create_summary()


if __name__ == "__main__":
    main()
