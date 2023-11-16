import yaml
from pathlib import Path


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

    def configure_paths(self):
        """Configurable filepaths."""
        self.base_path = Path("/mnt/cup/labs/hasson/247/subjects/") / self.sid
        self.filenames = {
            "audio_downsampled": self.base_path
            / "audio/audio-512Hz/{sid}_Part{part}_audio-512Hz.wav",
            "audio_deid": self.base_path
            / "audio/audio-deid/{sid}_Part{part}_audio-deid.wav",
            "audio_transcribe": self.base_path
            / "audio/audio-transcribe/{sid}_Part{part}_audio-transcribe.wav",
            "ecog_raw": self.base_path / "ecog/ecog-raw/{sid}_Part{part}_ecog-raw.EDF",
            "ecog_processed": self.base_path
            / "ecog/ecog-processed/{sid}_Part{part}_ecog-processed.EDF",
            "transcript": self.base_path / "transcript/xml/",
            "log": self.base_path / "log/",
            "silence": self.base_path / "notes/deid/{sid}_Part{part}_silences.csv",
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
