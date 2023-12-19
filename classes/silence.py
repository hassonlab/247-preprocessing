import pandas as pd
from autologging import traced, logged


@traced
@logged
class Silence:
    """File containing marked silences corresponding to a specific audio file.

    ...

    Attributes:
        file (PosixPath): Path to the silence file.
    """

    type = 'silences'
    ext = '.csv'

    def __init__(self, file):
        """Initializes the instance based on file identifier.

        Args:
          file (PosixPath): Path to file.
        """
        self.file = file

    def read_silence(self):
        """Read silence file to Pandas DataFrame"""
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
        """Convert times in table to timedelta"""
        self.silence_onsets = pd.to_timedelta(
            self.silences.onset_min, unit="m"
        ) + pd.to_timedelta(self.silences.onset_sec, unit="s")
        self.silence_offsets = pd.to_timedelta(
            self.silences.offset_min, unit="m"
        ) + pd.to_timedelta(self.silences.offset_sec, unit="s")
