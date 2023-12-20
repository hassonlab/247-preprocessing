<a id="classes/transcript"></a>

# classes/transcript

<a id="classes/transcript.Transcript"></a>

## Transcript Objects

```python
@traced

@logged
class Transcript()
```

Transcript corresponding to a specific audio file.

...

**Attributes**:

- `file` _PosixPath_ - Path to the transcript.

<a id="classes/transcript.Transcript.__init__"></a>

#### \_\_init\_\_

```python
def __init__(sid: str, file)
```

Initializes the instance based on file identifier.

**Arguments**:

- `file` _PosixPath_ - Path to the transcript.

<a id="classes/transcript.Transcript.parse_xml"></a>

#### parse\_xml

```python
def parse_xml()
```

Convert Verbit.AI format to our format.

<a id="classes/transcript.Transcript.get_audio_info_csv"></a>

#### get\_audio\_info\_csv

```python
def get_audio_info_csv() -> tuple([str, str])
```

Get audio onset date, time, duration from a CSV file.

Note: this function should only be used if this information is not in the header of the audio file.

<a id="classes/transcript.Transcript.agg_silences"></a>

#### agg\_silences

```python
def agg_silences(silence_file)
```

Add silence information to transcript.

**Arguments**:

- `silence_file` _DataFrame_ - Silence types, onsets, offsets.

<a id="classes/transcript.Transcript.add_dt"></a>

#### add\_dt

```python
def add_dt(onset_day: str, onset_time: str)
```

Add audio date-time inofrmation.

**Arguments**:

  onset_day (str)
  onset_time (str)

<a id="classes/transcript.Transcript.convert_timedelta"></a>

#### convert\_timedelta

```python
def convert_timedelta()
```

Convert to timedelta.

<a id="classes/transcript.Transcript.compress_transcript"></a>

#### compress\_transcript

```python
def compress_transcript(factor)
```

Compress transcript.

**Arguments**:

- `factor` _float_ - how much to compress times by.

