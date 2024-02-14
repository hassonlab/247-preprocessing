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


def subject_prep(subject_n: Subject):
    """Set-up for processing new subject"""

    # Create parent directory for subject
    if not subject_n.base_path.exists():
        subject_n.create_dir()

    # TODO: IMPORTANT: Additional checks to make sure order is correct when sorting

    # Transfer files
    subject_n.transfer_files()

    subject_n.edf_list()
    # Adjust file names for consistency
    for part, file in enumerate(sorted(subject_n.edf_files)):
        subject_n.rename_files(
            file.parents[1], file, str(part + 1).zfill(3), "ecog_raw", rename=True
        )
        # At this point, the directory should be empty and can be removed
        while file.exists():
            time.sleep(1)
        file.parents[0].rmdir()

    # NOTE: We can get the correct naming when we run downsampling/deid on nyu server
    for part, file in enumerate(sorted(subject_n.audio_512_files)):
        subject_n.rename_files(
            file.parents[1],
            file,
            str(part + 1).zfill(3),
            "audio_downsampled",
            rename=True,
        )

        # TODO: needs more testing
        while any(file.parents[0].iterdir()):
            time.sleep(1)
        file.parents[0].rmdir()

    for part, file in enumerate(sorted(subject_n.audio_deid_files)):
        subject_n.rename_files(
            file.parents[0], file, str(part + 1).zfill(3), "audio_deid", rename=True
        )

    subject_n.silence_list()
    for part, file in enumerate(sorted(subject_n.silence_files)):
        subject_n.rename_files(
            file.parents[0], file, str(part + 1).zfill(3), "silence", rename=True
        )


def ecog_prep(ecog_file: Ecog):
    """Split and process ECoG signal"""
    ecog_file.read_EDFHeader()
    ecog_file.end_datetime()
    ecog_file.read_channels(10, 100000, start=0, end=10)

    # TODO: Figure out how we're splitting files
    ecog_file.process_ecog()
    ecog_file.name = "".join([ecog_file.sid, "_ecog-raw_", "0", ".edf"])
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
    nyu_id = args.nyu_id
    new_id = args.sid
    steps = args.steps

    # Create config
    config = Config(new_id, nyu_id)
    config.configure_paths_old()
    config.configure_paths_nyu()

    # Generate instance of subject class
    subject_n = Subject(new_id, create_config=True)
    subject_n.filenames = config.filenames
    subject_n.__dict__.update(config.nyu_paths.items())
    # TODO: decide what to do with Subject

    # Get list of files to loop over for processing
    subject_n.audio_list()
    subject_n.edf_list()

    # Step_002: subject_prep: Prepare file structure, transfer files for processing new patient
    if "2" in steps:
        subject_prep(subject_n)
    else:
        print("Skipping step_002: subject_prep")

    logging.basicConfig(
        level=TRACE,
        filename=(config.filenames["log"] / "sub.log"),
        format="%(asctime)s %(levelname)s:%(name)s:%(funcName)s:%(message)s",
    )

    config.write_config_old()

    # Create subject-level transcript to append to
    subject_n.create_subject_transcript()

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
