<a id="classes/ecog"></a>

# classes/ecog

<a id="classes/ecog.Ecog"></a>

## Ecog Objects

```python
@traced

@logged
class Ecog()
```

Information and data for each patient ECoG file.

...

**Attributes**:

- `sid` _str_ - The unique subject indentifier.
- `file` _str_ - Name of edf file.
- `base_path` _PosixPath_ - Subject base directory.
- `audio_512_path` _PosixPath_ - Subject downsampled audio directory.
- `audio_deid_path` _PosixPath_ - Subject de-identified audio directory.
- `ecog_raw_path` _PosixPath_ - Subject raw EDF directory.
- `ecog_processed_path` _PosixPath_ - Subject processed EDF directory.
- `non_electrode_id` _:obj:`list` of :obj:`str`_ - Which channel labels are not electrodes.
- `expected_sr` _int_ - Expected sampling rate.
- `name` _str_ - EDF filename.
  
- `ecog_hdr` _dict_ - EDF header data.
- `samp_rate` _int_ - Sampling rate of electrode channels.
- `edf_enddatetime` _datetime_ - End date time of EDF file.
- `data` _NumPy array_ - EDF channel data.

<a id="classes/ecog.Ecog.__init__"></a>

#### \_\_init\_\_

```python
def __init__(config_type: str, sid: str, file)
```

Initializes the instance based on subject identifier and file identifier.

**Arguments**:

- `sid` _str_ - Identifies subject.
- `file` _str_ - Filename.

<a id="classes/ecog.Ecog.read_EDFHeader"></a>

#### read\_EDFHeader

```python
def read_EDFHeader()
```

Read EDF header.

<a id="classes/ecog.Ecog.end_datetime"></a>

#### end\_datetime

```python
def end_datetime()
```

Calculate EDF end datetime from start datetime and file duration.

<a id="classes/ecog.Ecog.read_channels"></a>

#### read\_channels

```python
def read_channels(onset_sec, offset_sec, **chan)
```

Read EDF channels for a certain time frame.

**Arguments**:

- `onset_sec` _int_ - Beginning of time frame to read.
- `offset_sec` _int_ - End of time frame to read.
- `**chan` - Keyword arguments 'start' and/or 'end'.

<a id="classes/ecog.Ecog.process_ecog"></a>

#### process\_ecog

```python
def process_ecog()
```

Process signal data.

<a id="classes/ecog.Ecog.write_edf"></a>

#### write\_edf

```python
def write_edf()
```

Write EDF file.

