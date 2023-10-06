"""Class: subject and Subclasse: ecog, audio, and transcript definitions.

...

Typical usage example:

  subject_n = subject()
  subject_n.create_dir()
"""

import socket
import json
import logging
import getpass
import subprocess
import pyedflib
import warnings
import taglib
import re
import math
import timeit
import numpy as np
import datetime as dt
import pandas as pd
import xml.etree.ElementTree as ET
from pathlib import Path
from pydub import AudioSegment
from multiprocessing import Pool

# import tracemalloc
# import timeit
# from scipy.io import wavfile
# from pydub.playback import play
# from pydub.utils import mediainfo
# from collections import deque
# import globus_sdk
# from globus_sdk.scopes import TransferScopes


class Subject:
    """Information about a patient.

    Aggregates information about data collected for a given patient.

    Attributes:
        sid: The unique subject indentifier, DType: string.
        base_path: Subject base directory, DType: Posix path.
        audio_512_path: Subject downsampled audio directory, DType: Posix path.
        audio_deid_path: Subject de-identified audio directory, DType: Posix path.
        ecog_raw_path: Subject raw EDF directory, DType: Posix path.
        ecog_processed_path: Subject processed EDF directory, DType: Posix path.
    """

    def __init__(self, sid: str):
        """Initializes the instance based on subject identifier.

        Args:
          sid: Identifies subject, Dtype: string.
        """
        self.sid = sid

        host = socket.gethostname()

        if host == "scotty.pni.Princeton.EDU":
            self.base_path = Path("/mnt/cup/labs/hasson/247/subjects") / self.sid
        else:
            self.base_path = Path("/Volumes/hasson/247/subjects/") / self.sid

        # self.base_path = Path('/Users/baubrey/Documents/pipeline/subjects/' + self.sid)
        self.audio_512_path = self.base_path / "audio/audio-512Hz/"
        self.audio_deid_path = self.base_path / "audio/audio-deid/"
        self.audio_transcribe_path = self.base_path / "audio/audio-transcribe/"
        self.ecog_raw_path = self.base_path / "ecog/ecog-raw/"
        self.ecog_processed_path = self.base_path / "ecog/ecog-processed/"
        self.silence_path = self.base_path / "notes/de-id/"
        self.transcript_path = self.base_path / "transcript/"

    def update_log(self, message: str):
        """Update logger for each step in the pipeline.

        Args:
          message: message written to log file, DType: string.
        """
        logging.basicConfig(
            filename=(self.base_path / "log/example.log"),
            level=logging.INFO,
            format="%(asctime)s %(message)s",
        )
        logging.info(message + ", User: %s", getpass.getuser())

        # start = timeit.default_timer()
        # tracemalloc.start()
        # current = tracemalloc.get_traced_memory()
        # print(current)
        # tracemalloc.stop()
        # stop = timeit.default_timer()

        # print('Time: ', stop - start)

    def audio_list(self):
        """Retruns list of audio files present in subject directory."""
        audio_512_files = [
            f for f in self.audio_512_path.rglob("[!.]*/*") if f.is_file()
        ]
        self.audio_512_files = audio_512_files

        audio_deid_files = [
            f for f in self.audio_deid_path.rglob("[!.]*") if f.is_file()
        ]
        self.audio_deid_files = audio_deid_files

    def edf_list(self):
        """Retruns list of EDF files present in subject directory."""
        # TODO: I don't know if this is consistant across subject (on nyu server)
        # self.edf_files = [f for f in self.ecog_raw_path.rglob("[!.]*/*")]
        self.edf_files = [f for f in self.ecog_raw_path.rglob("[!.]*")]
        # self.ecog_raw_path = self.ecog_raw_path

    def make_edf_wav_dict(self):
        self.alignment = {
            k.name: {"onset": {}, "offset": {}, "audio_files": {}}
            for k in self.edf_files
        }

    def transcript_list(self):
        """Retruns list of xml transcript files present in subject directory."""
        xml_files = [
            f for f in (self.transcript_path / "xml/").rglob("[!.]*") if f.is_file()
        ]
        self.xml_files = xml_files

    def create_subject_transcript(self):
        self.transcript = pd.DataFrame(
            columns=[
                "token_type",
                "token",
                "onset",
                "offset",
                "speaker",
                "utterance_idx",
            ]
        )

    def create_summary(self):
        """Create summary file for new patient, written to throughout pipeline."""
        with open(
            self.base_path / self.sid + "-summary.json", "w", encoding="utf-8"
        ) as f:
            json.dump(edf_wav_dict, f, ensure_ascii=False, indent=4)

    def create_dir(self):
        """Create directory and standard sub-directories for a new subject."""
        self.audio_512_path.mkdir(parents=True)
        self.audio_deid_path.mkdir(parents=True)
        self.audio_transcribe_path.mkdir(parents=True)
        self.ecog_raw_path.mkdir(parents=True)
        self.ecog_processed_path.mkdir(parents=True)
        (self.base_path / "log").mkdir(parents=True)
        (self.base_path / "anat").mkdir(parents=True)
        (self.base_path / "issue").mkdir(parents=True)
        (self.base_path / "notes").mkdir(parents=True)
        (self.base_path / "transcript/xml").mkdir(parents=True)

    def transfer_files(self, filetypes: list = ["ecog", "audio-512Hz", "audio-deid"]):
        """Transfer files to patient directory.

        Connect to Globus Transfer API and transfer files from NYU endpoint
        to Princeton endpoint.

        Args:
          filetypes: Which files to transfer, Dtype: list.
        """
        # We use Globus Transfer API to transfer large EDF files
        # Using Globus-CLI works, but there's probably a better way to do this

        # Fill in
        source_endpoint_id = "28e1658e-6ce6-11e9-bf46-0e4a062367b8:"
        dest_endpoint_id = "6ce834d6-ff8a-11e6-bad1-22000b9a448b:"

        globus_cmd = " ".join(
            [
                "globus",
                "login;",
                "globus",
                "endpoint",
                "activate",
                "--web",
                "6ce834d6-ff8a-11e6-bad1-22000b9a448b",
            ]
        )
        subprocess.run(globus_cmd, shell=True)

        # TODO: fix this
        for filetype in filetypes:
            if filetype == "audio-512Hz":
                source_path = Path(self.nyu_id) / "ZoomAudioFilesDownsampled/"
                dest_path = self.base_path / "audio/audio-512Hz/"
            elif filetype == "ecog":
                source_path = Path(self.nyu_id) / "Dayfiles/"
                dest_path = self.base_path / "ecog/ecog-raw/"
            elif filetype == "audio-deid":
                source_path = Path(self.nyu_id) / "DeidAudio/DeidAudio/"
                dest_path = self.base_path / "audio/audio-deid/"

            # id_cmd = " ".join(["globus", "task", "generate-submission-id"])
            # sub_id = (
            #    subprocess.check_output(id_cmd, shell=True)
            #    .decode("utf-8")
            #    .replace("\n", "")
            # )

            transfer_cmd = " ".join(
                [
                    "globus",
                    "transfer",
                    "-r",
                    source_endpoint_id + str(source_path),
                    dest_endpoint_id + str(dest_path),
                    "--jmespath",
                    "task_id",
                    "--format=UNIX",
                ]
            )

            tsk = (
                subprocess.check_output(transfer_cmd, shell=True)
                .decode("utf-8")
                .replace("\n", "")
            )

            # TODO: instead of waiting for each one, should submit all then wait
            wait_cmd = " ".join(["globus", "task", "wait", tsk])
            subprocess.run(wait_cmd, shell=True)

    def rename_files(self, newpath, part: str, file: Path, type: str, ext: str):
        """Rename and/or move files.

        ...

        Attributes:
            part: file identifier, DType: str.
            file: file path, DType: PosixPath.
            type: label indicating file type: DType: str.
            ext: file extension: DType: str.
        """
        # Ecog and downsampled audio files are not transferred with correct names
        # TODO: What do we want to do with multiple audio tracks?

        # TODO: Make this an attribute of Subject?
        txt = "{sid}_Part{part}_{type}.{ext}"
        # rename files and move directory
        file.rename(
            newpath
            / txt.format(
                sid=self.sid,
                part=part,
                type=type,
                ext=ext,
            )
        )


class Ecog(Subject):
    """Information and data for each patient ECoG file.

    ...

    Attributes:
        sid: A string indicating the unique subject indentifier.
        file: Name of edf file, DType: string.
        base_path: A pathlib PosixPath object pointing to the subject base directory.
        audio_512_path: A pathlib PosixPath object pointing to the subject downsampled audio directory.
        audio_deid_path: A pathlib PosixPath object pointing to the subject de-identified audio directory.
        ecog_raw_path: A pathlib PosixPath object pointing to the subject raw EDF directory.
        ecog_processed_path: Subject processed EDF directory, DType: Posix path.
        non_electrode_id: A list of strings indicating which channel labels are not electrodes.
        expected_sr: Integer of expected sampling rate.
        name: A string of the EDF file name.

        ecog_hdr: EDF header data, DType: dict.
        samp_rate: Sampling rate of electrode channels, DType: int.
        edf_enddatetime: End date time of EDF file, DYype: datetime.
        data: EDF channel data, DType: numpy array. (?)
    """

    def __init__(self, sid: str, file):
        """Initializes the instance based on subject identifier and file identifier.

        Args:
          sid: Identifies subject, DType: string.
        """

        # Inherit __init__ from patient super class (file directories).
        Subject.__init__(self, sid)
        self.name = file
        self.non_electrode_id = ["SG", "EKG", "DC"]

    expected_sr = 512

    # warnings.simplefilter("ignore")

    def read_EDFHeader(self):
        """Read EDF header."""
        self.ecog_hdr = pyedflib.highlevel.read_edf_header(
            str(self.ecog_raw_path / self.name), read_annotations=True
        )
        self.samp_rate = int(self.ecog_hdr["SignalHeaders"][0]["sample_rate"])

    def end_datetime(self):
        """Calculate EDF end datetime from start datetime and file duration."""
        # edf_dur_seconds = self.nRecords*self.recDurSec
        edf_duration = dt.timedelta(seconds=self.ecog_hdr["Duration"])
        self.edf_enddatetime = self.ecog_hdr["startdate"] + edf_duration

    def read_channels(self, onset_sec, offset_sec, **chan):
        """Read EDF channels for a certain time frame.

        Args:
            onset_sec: Beginning of time frame to read, DType: int.
            offset_sec: End of time frame to read, DType: int.
        """

        # If channels not specified on function call, read all channels
        if not chan["start"]:
            chan["start"] = 0
        if not chan["end"]:
            chan["end"] = len(self.ecog_hdr["channels"])

        chan_nums = range(chan["start"], chan["end"])

        num_samps = offset_sec * self.samp_rate - onset_sec * self.samp_rate
        data = np.empty([chan["end"] - chan["start"], num_samps])

        ecog_data = pyedflib.EdfReader(str(self.ecog_raw_path / self.name))
        for idx, chan in enumerate(chan_nums):
            # TODO: parallelize
            data[idx] = ecog_data.readSignal(
                chan,
                onset_sec,
                (offset_sec * self.samp_rate - onset_sec * self.samp_rate),
            )
        self.data = data
        ecog_data.close()

    def process_ecog(self):
        """Process signal data."""
        return

    def write_edf(self):
        """Write EDF file."""

        signal_hdrs = self.ecog_hdr["SignalHeaders"]
        del self.ecog_hdr["SignalHeaders"]
        # phys min and max are swapped for some reason
        for idx, hdr in enumerate(signal_hdrs):
            if hdr["physical_min"] > hdr["physical_max"]:
                signal_hdrs[idx]["physical_min"] = -(hdr["physical_min"])
                signal_hdrs[idx]["physical_max"] = -(hdr["physical_max"])

        # Suppress warnings from edfwriter
        warnings.filterwarnings(
            action="ignore", category=UserWarning, module=r".*edfwriter"
        )

        # Temp name (?) with datetime
        outname = str(self.ecog_processed_path / self.name)
        pyedflib.highlevel.write_edf(
            outname, self.data, signal_hdrs, header=self.ecog_hdr
        )


class Audio(Subject):
    """Information and data for each patient audio file.

    ...

    Attributes:
        sid: Unique subject indentifier, DType: str.
        name: Name of audio file, DType: str.
        base_path: Subject base directory, DType: PosixPath.
        audio_deid_path: Subject de-identified audio directory, DType: PosixPath.
        audio_transcribe_path: Subject transcription audio directory, DType: PosixPath.
        deid_audio: Data from de-identified audio file (input audio), DType: Pydub AudioSegment.
        transcribe_audio: Audio data for transcription (output audio), DType: Pydub AudioSegment.
    """

    def __init__(self, sid: str, file):
        """Initializes the instance based on file identifier.

        Args:
          fid: File identifier.
        """
        # Inherit __init__ from patient super class.
        Subject.__init__(self, sid)
        self.name = file

    def read_audio(self):
        """Read audio signal.

        Args:
          filepath: Path to audio file.
        """
        # TODO: option for reading multiple tracks?
        self.deid_audio = AudioSegment.from_wav(self.audio_deid_path / self.name)
        # play(audioPart)
        # NOTE: pydub does things in milliseconds

    def crop_audio(self, silence_fname):
        """Remove marked segments from audio. For uploading for transcription."""
        # TODO: The deid audio files might be split parts
        # TODO: Do more checks
        silences = pd.read_csv(
            silence_fname,
            header=None,
            names=[
                "onset_min",
                "onset_sec",
                "offset_min",
                "offset_sec",
                "silence_type",
            ],
        )

        # Change silence times to milliseconds
        silence_onsets = []
        silence_offsets = []
        for _, row in silences.iterrows():
            onset_ms = 1000 * ((row.onset_min * 60) + row.onset_sec)
            offset_ms = 1000 * ((row.offset_min * 60) + row.offset_sec)
            silence_onsets.append(onset_ms)
            silence_offsets.append(offset_ms)

        # Get speech times from silence times
        speech_onsets = np.array(silence_offsets)
        speech_offsets = np.roll(silence_onsets, -1)

        # Remove consecutive non-speech labels
        speech_idxs = np.where((speech_offsets - speech_onsets) != 0)
        speech_times = zip(speech_onsets[speech_idxs], speech_offsets[speech_idxs])
        # Concat segments
        crop_audio = AudioSegment.empty()
        for time in speech_times:
            crop_audio += self.deid_audio[time[0] : time[1]]
        self.transcribe_audio = crop_audio

    def slow_audio(self):
        """Slow down audio for transcription."""

        # slow_speed = 0.95
        # y_slow = librosa.effects.time_stretch(y, rate=slow_speed)
        sfaud = self.transcribe_audio._spawn(
            self.transcribe_audio.raw_data,
            overrides={"frame_rate": int(self.transcribe_audio.frame_rate * 0.95)},
        ).set_frame_rate(self.transcribe_audio.frame_rate)
        # sfaud = sound_with_altered_frame_rate.set_frame_rate(self.audioTrack.frame_rate)
        # breakpoint()
        self.transcribe_audio = sfaud

    def write_audio(self):
        """Write audio signal."""
        self.transcribe_audio.export(
            self.audio_transcribe_path / self.name, format="wav"
        )
        with taglib.File(
            self.audio_deid_path / self.name, save_on_exit=True
        ) as audio_file:
            audio_file.tags["startDateTime"] = "startDateTime"
            audio_file.tags["endDateTime"] = "endDateTime"


class Transcript(Subject):
    """Transcript corresponding to a specific audio file.

    ...

    Attributes:
        fid: A pathlib PosixPath object pointing to the transcript.
    """

    def __init__(self, sid: str, file):
        # Inherit __init__ from patient super class.
        Subject.__init__(self, sid)
        self.name = file

    def parse_xml(self):
        """Convert Verbit.AI format to our format."""
        # Empty list to append to
        transcript = []
        # Increase utterance count for every new utterance
        utterance_idx = -1
        # Punctuation we want to split and maintain from tokens
        punc = "([. |, |! |?])"
        # get element tree
        tree = ET.parse(self.transcript_path / "xml/" / self.name)
        root = tree.getroot()

        # Speaker will be 'Unknown' if the first line doesn't contain a speaker label,
        # else speaker label is maintained from previous line.
        speaker = "Unknown"
        # loop through and index into relevant children
        for child in root.findall(
            ".//{http://www.w3.org/2006/10/ttaf1}div/{http://www.w3.org/2006/10/ttaf1}p"
        ):
            text = child.text
            onset = child.attrib["begin"]
            offset = child.attrib["end"]

            # This is an empy line. It might be the case that the next line has both words (?)
            if text == None:
                continue

            if "[" in text:
                # Remove whitespace inside square brackets so we don't split a single tag
                start_idx = text.index("[")
                end_idx = text.index("]") + 1
                text = (
                    text[:start_idx]
                    + text[start_idx:end_idx].replace(" ", "")
                    + text[end_idx:]
                )

            # Split if multiple tokens in line
            line = text.split(" ")

            # '>>' indicates new utterance
            if line[0] == ">>":
                utterance_idx += 1
                del line[0]

                # Update speaker
                label_break = [idx for idx, s in enumerate(line) if ":" in s]
                if label_break:
                    speaker = "".join(line[: label_break[0] + 1]).replace(":", "")
                    del line[: label_break[0] + 1]
            for elem in line:
                # Split if contains punctuation
                tokens = re.split(punc, elem)
                for token in tokens:
                    # Square brackets indicates tag
                    if "[" in token:
                        token_type = "tag"
                    elif token in punc:
                        token_type = "punctuation"
                        # TODO: Does the punctuation we want always come at the end of line?
                        del tokens[-1]
                    else:
                        token_type = "word"
                    # List for this line
                    line_list = [
                        token_type,
                        token,
                        onset,
                        offset,
                        speaker,
                        utterance_idx,
                    ]
                    # Append to full part transcript
                    transcript.append(line_list)

        self.transcript = pd.DataFrame(
            transcript,
            columns=[
                "token_type",
                "token",
                "onset",
                "offset",
                "speaker",
                "utterance_idx",
            ],
        )
        # TODO: Decide what to do with the 'Multiple Speaker' tag
        # TODO: Checks for additional punctuation: '--'

    def agg_silences(self, silence_fname):
        # TODO: the audio cropping function should match this.

        # Silence times to timedelta
        silences = pd.read_csv(
            silence_fname,
            header=None,
            names=[
                "onset_min",
                "onset_sec",
                "offset_min",
                "offset_sec",
                "silence_type",
            ],
        )

        silence_onsets = pd.to_timedelta(
            silences.onset_min, unit="m"
        ) + pd.to_timedelta(silences.onset_sec, unit="s")
        silence_offsets = pd.to_timedelta(
            silences.offset_min, unit="m"
        ) + pd.to_timedelta(silences.offset_sec, unit="s")

        # TODO: speaker and utterance_idx should be inherited where the silence type is not no speech.
        for onset, offset in zip(silence_onsets, silence_offsets):
            self.transcript.loc[
                self.transcript.onset > self.origin + onset, ["onset", "offset"]
            ] += (offset - onset)

        # TODO: consider separating retiming and adding silences to transcript for flexibility.
        rep_val = len(silences.silence_type)
        silence_df = pd.DataFrame(
            {
                "token_type": ["silence"] * rep_val,
                "token": silences.silence_type,
                "onset": self.origin + silence_onsets,
                "offset": self.origin + silence_offsets,
                "speaker": [None] * rep_val,
                "utterance_idx": [None] * rep_val,
            }
        )

        self.transcript = (
            pd.concat([self.transcript, silence_df])
            .sort_values(by="onset")
            .reset_index(drop=True)
        )

    def add_dt(self, onset_day, onset_time):
        """Add audio date-time inofrmation."""

        # TODO: Consider moving this for flexibility
        self.origin = pd.Timestamp(" ".join([onset_day, onset_time]))

        # To timestamps based on origin (onset date-time of audio file)
        self.transcript.onset += self.origin
        self.transcript.offset += self.origin

    def convert_timedelta(self):
        self.transcript.onset = pd.to_timedelta(self.transcript.onset)
        self.transcript.offset = pd.to_timedelta(self.transcript.offset)

    def compress_transcript(self, factor):
        # Adjust for 5% slow down
        self.transcript.onset = self.transcript.onset - self.transcript.onset * factor
        self.transcript.offset = (
            self.transcript.offset - self.transcript.offset * factor
        )
