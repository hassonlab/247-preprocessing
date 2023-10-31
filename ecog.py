import pyedflib
import warnings
import numpy as np
import datetime as dt
from multiprocessing import Pool


class Ecog:
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

    def __init__(self, config_type: str, sid: str, file):
        """Initializes the instance based on subject identifier and file identifier.

        Args:
          sid: Identifies subject, DType: string.
        """

        # Inherit __init__ from patient super class (file directories).
        # Subject.__init__(self, sid)
        self.sid = sid
        self.name = file
        self.non_electrode_id = ["SG", "EKG", "DC"]

    expected_sr = 512

    # warnings.simplefilter("ignore")

    def read_EDFHeader(self):
        """Read EDF header."""
        self.ecog_hdr = pyedflib.highlevel.read_edf_header(
            str(self.in_path / self.name), read_annotations=True
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

        ecog_data = pyedflib.EdfReader(str(self.in_path / self.name))
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
