<a id="classes/audio"></a>

# classes/audio

<a id="classes/audio.Audio"></a>

## Audio Objects

```python
@traced

@logged
class Audio()
```

Information and data for each patient audio file.

...

**Attributes**:

- `sid` - Unique subject indentifier, DType: str.
- `name` - Name of audio file, DType: str.
- `base_path` - Subject base directory, DType: PosixPath.
- `audio_deid_path` - Subject de-identified audio directory, DType: PosixPath.
- `audio_transcribe_path` - Subject transcription audio directory, DType: PosixPath.
- `deid_audio` - Data from de-identified audio file (input audio), DType: Pydub AudioSegment.
- `transcribe_audio` - Audio data for transcription (output audio), DType: Pydub AudioSegment.

<a id="classes/audio.Audio.__init__"></a>

#### \_\_init\_\_

```python
def __init__(sid: str, file)
```

Initializes the instance based on file identifier.

**Arguments**:

- `fid` - File identifier.

<a id="classes/audio.Audio.read_audio"></a>

#### read\_audio

```python
def read_audio()
```

Read audio signal.

**Arguments**:

- `filepath` - Path to audio file.

<a id="classes/audio.Audio.crop_audio"></a>

#### crop\_audio

```python
def crop_audio(silence_times)
```

Remove marked segments from audio. For uploading for transcription.

<a id="classes/audio.Audio.slow_audio"></a>

#### slow\_audio

```python
def slow_audio()
```

Slow down audio for transcription.

<a id="classes/audio.Audio.write_audio"></a>

#### write\_audio

```python
def write_audio()
```

Write audio signal.

