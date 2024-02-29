
ECoG Preparation
================
  
The ecog_prep function in [pipeline_247.py](pipeline_247.py) defines the substeps for preparing ECoG data.
# Code Walkthrough


```python
def ecog_prep(ecog_file: Ecog):
    """Split and process ECoG signal"""
    ecog_file.read_EDFHeader()
    ecog_file.end_datetime()
    ecog_file.read_channels(10, 100000, start=0, end=10)

    # TODO: Figure out how we're splitting files
    ecog_file.process_ecog()
    ecog_file.name = "".join([ecog_file.sid, "_ecog-raw_", "0", ".edf"])
    ecog_file.write_edf()

```
## Read header from EDF file.
  
For more information about EDF headers, see the [Wiki](../../wiki/Data-Descriptions#electrocorticography-ecog)

```python
ecog_file.read_EDFHeader()
```

```python
    def read_EDFHeader(self):
        """Read EDF header."""
        self.ecog_hdr = pyedflib.highlevel.read_edf_header(
            str(self.name), read_annotations=True
        )
        self.samp_rate = int(self.ecog_hdr["SignalHeaders"][0]["sample_rate"])

```
## Calculate EDF file end date and time.
  
[]()

```python
ecog_file.end_datetime()
```

```python
    def end_datetime(self):
        """Calculate EDF end datetime from start datetime and file duration."""
        # edf_dur_seconds = self.nRecords*self.recDurSec
        edf_duration = dt.timedelta(seconds=self.ecog_hdr["Duration"])
        self.enddate = self.ecog_hdr["startdate"] + edf_duration

```
## Read electrode data from EDF file.
  
Optionally specify start time, end time, and channels to read[]()

```python
ecog_file.read_channels(10, 100000, start=0, end=10)
```

```python
    def read_channels(self, onset_sec, offset_sec, **chan):
        """Read EDF channels for a certain time frame.

        Args:
            onset_sec (int): Beginning of time frame to read.
            offset_sec (int): End of time frame to read.
            **chan: Keyword arguments 'start' and/or 'end'.
        """

        def read_elec_signal(chn_idx):
            return ecog_data.readSignal(chn_idx, onset_sec, offset_sec)

        # If channels not specified on function call, read all channels
        if not chan["start"]:
            chan["start"] = 0
        if not chan["end"]:
            chan["end"] = len(self.ecog_hdr["channels"])

        chan_nums = range(chan["start"], chan["end"])

        num_samps = offset_sec * self.samp_rate - onset_sec * self.samp_rate

        # TODO: (IMPORTANT) Memory issue with large arrays
        data = np.empty([chan["end"] - chan["start"], num_samps])

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

```
## TODO
  
[]()

```python
ecog_file.process_ecog()
```

```python
    def process_ecog(self):
        """Process signal data."""
        return

```
## Name new EDF file according to the 24/7 naming convention [link]
  
[]()

```python
ecog_file.name = "".join([ecog_file.sid, "_ecog-raw_", "0", ".edf"])
```
## Write new EDF file
  
[]()

```python
ecog_file.write_edf()
```

```python
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
        outname = str(self.ecog_processed_path / self.name)
        pyedflib.highlevel.write_edf(
            outname, self.data, signal_hdrs, header=self.ecog_hdr
        )

```  
PyEDFlib: [https://pyedflib.readthedocs.io/en/latest/ref/highlevel.html](https://pyedflib.readthedocs.io/en/latest/ref/highlevel.html)