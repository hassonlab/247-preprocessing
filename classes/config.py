import yaml
import argparse
from pathlib import Path

# from configobj import ConfigObj
from configparser import ConfigParser, ExtendedInterpolation


class Config:
    def __init__(self, sid, nyu_id=None):
        """Initializes the instance based on subject identifier.

        Args:
          sid (str): Identifies subject.
          nyu_id (str, optional): Subject identifier on NYU server.
        """
        self.sid = sid
        if nyu_id:
            self.nyu_id = nyu_id

    def arg_parse():
        parser = argparse.ArgumentParser()
        parser.add_argument("--nyu_id", type=str)
        parser.add_argument("--sid", type=str)
        parser.add_argument("--input_name", nargs="*", default=None)
        parser.add_argument("--steps", nargs="*", default=["2", "3", "4", "5"])

        args = parser.parse_args()

        return args

    def write_config(self):
        # config = ConfigObj(interpolation='ConfigParser')
        config = ConfigParser(interpolation=ExtendedInterpolation())

        self.base_path = Path("/mnt/cup/labs/hasson/247/subjects/") / self.sid

        config.filename = self.base_path / "test.ini"
        config["file_id"] = file_id = {"sid": self.sid}
        config.sid = self.sid
        filenames = {
            "sid": self.sid,
            "audio_downsampled": self.base_path
            / "audio/audio-512Hz/{sid}_Part{part}_audio-512Hz.wav",
            "audio_deid": self.base_path
            / "audio/audio-deid/%(sid)s_Part%(part)s_audio-deid.wav",
            "audio_transcribe": self.base_path
            / "audio/audio-transcribe/%(sid)s_Part%(part)s_audio-transcribe.wav",
            "ecog_raw": self.base_path
            / "ecog/ecog-raw/%(sid)s_Part%(part)s_ecog-raw.EDF",
            "ecog_processed": self.base_path
            / "ecog/ecog-processed/%(sid)s_Part%(part)s_ecog-processed.EDF",
            "transcript": self.base_path / "transcript/xml/",
            "log": self.base_path / "log/",
            "silence": self.base_path / "notes/deid/%(sid)s_Part%(part)s_silences.csv",
            "anat": self.base_path / "anat/",
            "issue": self.base_path / "issue/",
        }

        nyu_base_path = Path(self.nyu_id)
        self.nyu_paths = {
            "nyu_base_path": nyu_base_path,
            "nyu_ecog_path": nyu_base_path / "Dayfiles/",
            "nyu_deid_audio_path": nyu_base_path / "DeidAudio/DeidAudio/",
            "nyu_downsampled_audio_path": nyu_base_path / "ZoomAudioFilesDownsampled/",
            "source_endpoint_id": "28e1658e-6ce6-11e9-bf46-0e4a062367b8",
            "dest_endpoint_id": "6ce834d6-ff8a-11e6-bad1-22000b9a448b",
        }

        config["filenames"] = filenames
        self.config = config
        # config.write()

    def read_config(self):
        config = ConfigObj(self.filename)

    def configure_paths_old(self):
        """Configurable filepaths."""
        self.base_path = Path("/mnt/cup/labs/hasson/247/subjects/") / self.sid
        self.filenames = {
            "audio_downsampled": self.base_path
            / "audio/audio-512Hz/{sid}_{part}_audio-512Hz.wav",
            "audio_deid": self.base_path
            / "audio/audio-deid/{sid}_{part}_audio-deid.wav",
            "audio_transcribe": self.base_path
            / "audio/audio-transcribe/{sid}_{part}_audio-transcribe.wav",
            "ecog_raw": self.base_path / "ecog/ecog-raw/{sid}_{part}_ecog-raw.EDF",
            "ecog_processed": self.base_path
            / "ecog/ecog-processed/{sid}_{part}_ecog-processed.EDF",
            "transcript": self.base_path
            / "transcript/xml/{sid}_{part}_verbit-transcript.xml",
            "log": self.base_path / "log/",
            "silence": self.base_path / "notes/deid/{sid}_{part}_silences.csv",
            "anat": self.base_path / "anat/",
            "issue": self.base_path / "issue/",
        }

    def configure_paths_nyu(self):
        """Configurable filepaths on NYU server."""
        nyu_base_path = Path(self.nyu_id)
        self.nyu_paths = {
            "nyu_base_path": nyu_base_path,
            "nyu_ecog_path": nyu_base_path / "Dayfiles/",
            "nyu_deid_audio_path": nyu_base_path / "DeidAudio/DeidAudio/",
            "nyu_deid_silence_path": nyu_base_path / "DeidAudio/DeidSpreadsheets/",
            "nyu_downsampled_audio_path": nyu_base_path / "ZoomAudioFilesDownsampled/",
            "source_endpoint_id": "28e1658e-6ce6-11e9-bf46-0e4a062367b8",
            "dest_endpoint_id": "6ce834d6-ff8a-11e6-bad1-22000b9a448b",
        }

    def write_config_old(self):
        """Write YAML file containing configured information for each subject."""
        with open(self.base_path / "test.yaml", "w") as file:
            yaml.dump(self, file)

    def read_config_old(self):
        """Read YAML file containing configured information for each subject."""
        with open(self.base_path / "test.yaml", "r") as file:
            # TODO: safe_load (?) might have to change how I'm writing the file
            self.config = yaml.load(file, Loader=yaml.BaseLoader)

    def config_steps(self):

        self.steps = {
            (1, "00_setup"): {1: "configure_princeton_paths", 2: "configure_nyu_paths"},
            (2, "01_subject_prep"): {
                1: "create_directories",
                2: "transfer_files",
                3: "edf_list",
            },
            (3, "02_ecog_prep"): {
                "iterate_on": "edf_list",
                1: "initiate_instance",
                2: "read_EDF_header",
            },
        }

        return
