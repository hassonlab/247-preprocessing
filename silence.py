import pandas as pd


class Silence:
    """Transcript corresponding to a specific audio file.

    ...

    Attributes:
        fid: A pathlib PosixPath object pointing to the transcript.
    """

    def __init__(self, file):
        # Inherit __init__ from patient super class.
        self.file = file

    def read_silence(self):
        self.silences = pd.read_csv(
            self.file,
            header=None,
            names=[
                "onset_min",
                "onset_sec",
                "offset_min",
                "offset_sec",
                "silence_type",
            ],
        )

    def calc_silence(self):
        self.silence_onsets = pd.to_timedelta(
            self.silences.onset_min, unit="m"
        ) + pd.to_timedelta(self.silences.onset_sec, unit="s")
        self.silence_offsets = pd.to_timedelta(
            self.silences.offset_min, unit="m"
        ) + pd.to_timedelta(self.silences.offset_sec, unit="s")
