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


def audio_prep(transcribe_audio: Audio, silence_times: Silence):
    """Prepare audio file for transcription"""
    transcribe_audio.read_audio()

    transcribe_audio.crop_audio(silence_times)
    transcribe_audio.slow_audio()
    # audio.denoise_audio(transcribe_audio)
    transcribe_audio.write_audio()


def transcript_prep(transcript_file: Transcript, silence_times: Silence):
    """Prepare subject-level transcript"""
    transcript_file.parse_xml()
    transcript_file.convert_timedelta()
    transcript_file.compress_transcript(0.05)

    onset_day, onset_time = transcript_file.get_audio_info_csv()
    transcript_file.add_dt(onset_day, onset_time)

    transcript_file.agg_silences(silence_times)


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
            fun(subject_n)

    breakpoint()

    logging.basicConfig(
        level=TRACE,
        filename=(config.filenames["log"] / "sub.log"),
        format="%(asctime)s %(levelname)s:%(name)s:%(funcName)s:%(message)s",
    )

    config.write_config_old()

    # Loop over files for processing
    for file in subject_n.edf_files:
        # Step_003: ecog_prep: Split EDF files, ECoG signal processing
        if "3" in steps:
            # TODO: IMPORTANT Find matching EDF file
            ecog_file = Ecog(args, file)
            ecog_prep(ecog_file)
        else:
            print("Skipping step_003: ecog_prep")
        # Step_004: audio_prep: Prepare audio file for transcription
        if "4" in steps:
            transcribe_audio = Audio(subject_n.sid, file)

            [_, part, _] = transcribe_audio.in_name.stem.split("_")
            transcribe_audio.out_name = subject_n.rename_files(
                file, part, "audio_transcribe"
            )

            silence_file = subject_n.rename_files(file, part, "silence")
            silence_times = Silence(silence_file)
            silence_times.read_silence()
            silence_times.calc_silence()

            audio_prep(transcribe_audio, silence_times)
        else:
            print("Skipping step_004: audio_prep")
        if "5" in steps:
            [_, part, _] = file.stem.split("_")
            transcript_filename = subject_n.rename_files(file, part, "transcript")
            # TODO: decide what to do about possible file mismatches (if we have an audio file but no transcript, etc.)
            if transcript_filename.is_file():
                transcript_file = Transcript(subject_n.sid, transcript_filename)

                if "silence_times" not in locals():
                    silence_file = subject_n.rename_files(file, part, "silence")
                    silence_times = Silence(silence_file)
                    silence_times.read_silence()
                    silence_times.calc_silence()

                transcript_prep(transcript_file, silence_times)

            subject_n.transcript = pd.concat(
                [subject_n.transcript, transcript_file.transcript]
            )
        else:
            print("Skipping step_005: transcript_prep")

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

    # TODO: move this to end
    # if not (subject_n.basePath / sid + '-summary.json').exists(): subject_n.create_summary()


if __name__ == "__main__":
    main()
