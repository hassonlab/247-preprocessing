import yaml
import argparse
from pathlib import Path

class Config:
    def __init__(self, sid: str) -> dict:
        """Initializes the instance based on subject identifier.

        Args:
          sid (str): Identifies subject.
          nyu_id (str, optional): Subject identifier on NYU server.
        """
        self.sid = sid

    def arg_parse():
        parser = argparse.ArgumentParser()
        parser.add_argument("--sid", type=str)
        parser.add_argument("--input_name", nargs="*", default=None)
        parser.add_argument(
            "--steps",
            nargs="*",
            default=["subject_prep", "ecog_prep", "audio_prep", "transcript_prep"],
        )

        args = parser.parse_args()

        return args

    def configure_paths_della(self):
        """Configurable filepaths."""
        #self.base_path = Path("/mnt/cup/labs/hasson/247/subjects/") / self.sid
        self.base_path = Path("/projects/HASSON/247/data/subjects/") / self.sid
        self.filenames = {
            "audio-512Hz": self.base_path
            / "audio/audio-512Hz/{sid}_Part{part}_audio-512Hz.wav",
            "audio-deid": self.base_path
            / "audio/audio-deid/{sid}_Part{part}_audio-deid.wav",
            "audio-transcribe": self.base_path
            / "audio/audio-transcribe/{sid}_Part{part}_audio-transcribe.wav",
            "ecog-raw": self.base_path / "ecog/ecog-raw/{sid}_Part{part}_ecog-raw.EDF",
            "ecog-processed": self.base_path
            / "ecog/ecog-processed/{sid}_Part{part}_ecog-processed.EDF",
            "transcript": self.base_path
            / "transcript/xml/{sid}_Part{part}_verbit-transcript.xml",
            "log": self.base_path / "log/",
            "silence": self.base_path / "notes/deid/{sid}_Part{part}_silences.csv",
            "elec-loc-MNI": self.base_path / "anat/{sid}_T1T2_coor_MNI.txt",
            "elec-loc-T1": self.base_path / "anat/{sid}_T1T2_coor_T1.txt",
            "elec-loc-T1": self.base_path / "anat/{sid}_T1T2_T1_AnatomicalRegions.txt",
            "issue": self.base_path / "issue/",
        }

    def configure_paths_nyu(self):
        """Configurable filepaths on NYU server."""
        nyu_base_path = Path("NY" + self.sid)
        self.nyu_paths = {
            "nyu_base_path": nyu_base_path,
            "nyu_ecog_path": nyu_base_path / "Dayfiles/",
            "nyu_deid_audio_path": nyu_base_path / "DeidAudio/DeidAudio/",
            "nyu_deid_silence_path": nyu_base_path / "DeidAudio/DeidSpreadsheets/",
            "nyu_downsampled_audio_path": nyu_base_path / "ZoomAudioFilesDownsampled/",
            "source_endpoint_id": "28e1658e-6ce6-11e9-bf46-0e4a062367b8",
            "dest_endpoint_id": "6ce834d6-ff8a-11e6-bad1-22000b9a448b",
        }

    def write_config(self):
        """Write YAML file containing configured information for each subject."""
        with open(self.base_path / "test.yaml", "w") as file:
            yaml.dump(self, file)

    def read_config(self):
        """Read YAML file containing configured information for each subject."""
        with open(self.base_path / "test.yaml", "r") as file:
            # TODO: safe_load (?) might have to change how I'm writing the file
            self.config = yaml.load(file, Loader=yaml.BaseLoader)
