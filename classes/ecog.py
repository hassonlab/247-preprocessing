import pyedflib
import warnings
import getpass
import numpy as np
import datetime as dt
import multiprocessing
import pandas as pd
from concurrent.futures import ThreadPoolExecutor
from autologging import traced, logged


@traced
@logged
class Ecog:
    """Information and data for each patient ECoG file.

    ...

    Attributes:
        sid (str): The unique subject indentifier.
        file (str): Name of edf file.
        base_path (PosixPath): Subject base directory.
        audio_512_path (PosixPath): Subject downsampled audio directory.
        audio_deid_path (PosixPath): Subject de-identified audio directory.
        ecog_raw_path (PosixPath): Subject raw EDF directory.
        ecog_processed_path (PosixPath): Subject processed EDF directory.
        non_electrode_id (:obj:`list` of :obj:`str`): Which channel labels are not electrodes.
        expected_sr (int): Expected sampling rate.
        name (str): EDF filename.

        ecog_hdr (dict): EDF header data.
        samp_rate (int): Sampling rate of electrode channels.
        edf_enddatetime (datetime): End date time of EDF file.
        data (NumPy array): EDF channel data.
    """

    def __init__(self, sid, filename):
        """Initializes the instance based on subject identifier and file identifier.

        Args:
          sid (str): Identifies subject.
          file (str): Filename.
        """

        self.sid = sid
        self.name = filename
        self.non_electrode_id = ["SG", "EKG", "DC", "Pulse Rate"]

        self.__log.info("User: " + getpass.getuser())

    expected_sr = 512

    # warnings.simplefilter("ignore")

    def read_EDFHeader(self):
        """Read EDF header."""
        self.ecog_hdr = pyedflib.highlevel.read_edf_header(
            str(self.name), read_annotations=True
        )
        self.samp_rate = int(self.ecog_hdr["SignalHeaders"][0]["sample_rate"])

    def read_channel_loc(self, filename):

        channel_locs = pd.read_csv(filename)
        self.channel_locs = channel_locs

        return channel_locs
    
    def make_elec_loc_dict():

        keys = ["chan_idx",
                "elec_name_hdr",
                "elec_name_txt",
                "elec_coor_MNI",
                "elec_coor_T1",
                "elec_reg"]

        return

    def end_datetime(self):
        """Calculate EDF end datetime from start datetime and file duration."""
        # edf_dur_seconds = self.nRecords*self.recDurSec
        edf_duration = dt.timedelta(seconds=self.ecog_hdr["Duration"])
        self.enddate = self.ecog_hdr["startdate"] + edf_duration

    def read_channels(self, onset_sec, offset_sec, **chan):
        """Read EDF channels for a certain time frame.

        Args:
            onset_sec (int): Beginning of time frame to read.
            offset_sec (int): End of time frame to read.
            **chan: Keyword arguments 'start' and/or 'end'.
        """

        def read_elec_signal(chn_idx):
            return ecog_data.readSignal(chn_idx, onset_sec, offset_sec)

        # If channels not specified on function call, read all 
        if "chan_list" not in chan:
            if "start" not in chan:
                chan["start"] = 0
            if "end" not in chan:
                chan["end"] = len(self.ecog_hdr["channels"])
            chan_nums = range(chan["start"], chan["end"])
        elif "chan_list" in chan:
            chan_nums = chan["chan_list"]

        num_samps = offset_sec * self.samp_rate - onset_sec * self.samp_rate

        # TODO: (IMPORTANT) Memory issue with large arrays
        data = np.empty([len(chan_nums), num_samps])

        ecog_data = pyedflib.EdfReader(str(self.name))
        # for idx, chan in enumerate(chan_nums):
        #    # TODO: parallelize
        # data = ecog_data.readSignal(
        #        chan,
        #        onset_sec,
        #        (offset_sec * self.samp_rate - onset_sec * self.samp_rate),
        #    )
        # self.data = data
        # ecog_data.close()

        with ThreadPoolExecutor() as pool:
            data = np.stack(list(pool.map(read_elec_signal, chan_nums))).squeeze()

        self.data = data
        ecog_data.close()

    def process_ecog(self):
        """Process signal data."""
        return

    def write_edf(self):
        """Write EDF file."""

        signal_hdrs = self.ecog_hdr["SignalHeaders"]
        del self.ecog_hdr["SignalHeaders"]

        # TODO: move this
        # phys min and max are swapped for some reason (798)
        for idx, hdr in enumerate(signal_hdrs):
            if hdr["physical_min"] > hdr["physical_max"]:
                signal_hdrs[idx]["physical_min"] = -(hdr["physical_min"])
                signal_hdrs[idx]["physical_max"] = -(hdr["physical_max"])

        # Suppress warnings from edfwriter
        warnings.filterwarnings(
            action="ignore", category=UserWarning, module=r".*edfwriter"
        )

        # Temp name (?) with datetime
        outname = str(self.name)
        pyedflib.highlevel.write_edf(
            outname, self.data, signal_hdrs, header=self.ecog_hdr
        )
