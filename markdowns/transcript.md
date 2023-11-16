<a id="transcript"></a>

# transcript

<a id="transcript.Transcript"></a>

## Transcript Objects

```python
class Transcript()
```

Transcript corresponding to a specific audio file.

...

**Attributes**:

- `fid` - A pathlib PosixPath object pointing to the transcript.

<a id="transcript.Transcript.parse_xml"></a>

#### parse\_xml

```python
def parse_xml()
```

Convert Verbit.AI format to our format.

<a id="transcript.Transcript.add_dt"></a>

#### add\_dt

```python
def add_dt(onset_day, onset_time)
```

Add audio date-time inofrmation.

