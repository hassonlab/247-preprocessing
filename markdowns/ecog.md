<a id="ecog"></a>

# ecog

<a id="ecog.Ecog"></a>

## Ecog Objects

```python
class Ecog()
```

Information and data for each patient ECoG file.

...

**Attributes**:

- `sid` - A string indicating the unique subject indentifier.
- `file` - Name of edf file, DType: string.
- `base_path` - A pathlib PosixPath object pointing to the subject base directory.
- `audio_512_path` - A pathlib PosixPath object pointing to the subject downsampled audio directory.
- `audio_deid_path` - A pathlib PosixPath object pointing to the subject de-identified audio directory.
- `ecog_raw_path` - A pathlib PosixPath object pointing to the subject raw EDF directory.
- `ecog_processed_path` - Subject processed EDF directory, DType: Posix path.
- `non_electrode_id` - A list of strings indicating which channel labels are not electrodes.
- `expected_sr` - Integer of expected sampling rate.
- `name` - A string of the EDF file name.
  
- `ecog_hdr` - EDF header data, DType: dict.
- `samp_rate` - Sampling rate of electrode channels, DType: int.
- `edf_enddatetime` - End date time of EDF file, DYype: datetime.
- `data` - EDF channel data, DType: numpy array. (?)

<a id="ecog.Ecog.__init__"></a>

#### \_\_init\_\_

```python
def __init__(config_type: str, sid: str, file)
```

Initializes the instance based on subject identifier and file identifier.

**Arguments**:

- `sid` - Identifies subject, DType: string.

<a id="ecog.Ecog.read_EDFHeader"></a>

#### read\_EDFHeader

```python
def read_EDFHeader()
```

Read EDF header.

<a id="ecog.Ecog.end_datetime"></a>

#### end\_datetime

```python
def end_datetime()
```

Calculate EDF end datetime from start datetime and file duration.

<a id="ecog.Ecog.read_channels"></a>

#### read\_channels

```python
def read_channels(onset_sec, offset_sec, **chan)
```

Read EDF channels for a certain time frame.

**Arguments**:

- `onset_sec` - Beginning of time frame to read, DType: int.
- `offset_sec` - End of time frame to read, DType: int.

<a id="ecog.Ecog.process_ecog"></a>

#### process\_ecog

```python
def process_ecog()
```

Process signal data.

<a id="ecog.Ecog.write_edf"></a>

#### write\_edf

```python
def write_edf()
```

Write EDF file.

