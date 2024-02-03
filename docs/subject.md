<a id="classes/subject"></a>

# classes/subject

<a id="classes/subject.Subject"></a>

## Subject Objects

```python
@traced

@logged
class Subject()
```

Setup for a new patient.

Aggregates information about data collected for a given patient.

**Attributes**:

- `sid` _str_ - The unique subject indentifier.
- `base_path` _PosixPath_ - Subject base directory.
- `audio_512_path` _PosixPath_ - Subject downsampled audio directory.
- `audio_deid_path` _PosixPath_ - Subject de-identified audio directory.
- `ecog_raw_path` _PosixPath_ - Subject raw EDF directory.
- `ecog_processed_path` _PosixPath_ - Subject processed EDF directory.

<a id="classes/subject.Subject.__init__"></a>

#### \_\_init\_\_

```python
def __init__(sid: str, create_config=False)
```

Initializes the instance based on subject identifier.

**Arguments**:

- `sid` _str_ - Identifies subject.

<a id="classes/subject.Subject.update_log"></a>

#### update\_log

```python
def update_log(message: str)
```

Update logger for each step in the pipeline.

**Arguments**:

- `message` - message written to log file, DType: string.

<a id="classes/subject.Subject.audio_list"></a>

#### audio\_list

```python
def audio_list()
```

Retruns list of audio files present in subject directory.

<a id="classes/subject.Subject.edf_list"></a>

#### edf\_list

```python
def edf_list()
```

Retruns list of EDF files present in subject directory.

<a id="classes/subject.Subject.transcript_list"></a>

#### transcript\_list

```python
def transcript_list()
```

Retruns list of xml transcript files present in subject directory.

<a id="classes/subject.Subject.silence_list"></a>

#### silence\_list

```python
def silence_list()
```

Retruns list of csv files of de-identification notes present in subject directory.

<a id="classes/subject.Subject.make_edf_wav_dict"></a>

#### make\_edf\_wav\_dict

```python
def make_edf_wav_dict()
```

Start a dictionary for alignment between EDF and WAV files.

<a id="classes/subject.Subject.create_subject_transcript"></a>

#### create\_subject\_transcript

```python
def create_subject_transcript()
```

Create an empty, subject-level transcript that will be filled with each part-level transcript.

<a id="classes/subject.Subject.create_summary"></a>

#### create\_summary

```python
def create_summary()
```

Create summary file for new patient, written to throughout pipeline.

<a id="classes/subject.Subject.create_dir"></a>

#### create\_dir

```python
def create_dir()
```

Create directory and standard sub-directories for a new subject.

<a id="classes/subject.Subject.transfer_files"></a>

#### transfer\_files

```python
def transfer_files(
        filetypes: list = ["ecog", "audio-512Hz", "audio-deid", "silence"])
```

Transfer files to patient directory.

Connect to Globus Transfer API and transfer files from NYU endpoint
to Princeton endpoint.

**Arguments**:

- `filetypes` _list_ - Which files to transfer.

<a id="classes/subject.Subject.rename_files"></a>

#### rename\_files

```python
def rename_files(file: Path, part: str, type: str, rename=False)
```

Rename and/or move files.

...

**Attributes**:

- `newpath` _PosixPath_ - new path
- `part` _str_ - file identifier.
- `file` _PosixPath_ - file path.
- `part` _str_ - file part
- `type` _str_ - label indicating file type.
- `ext` _str_ - file extension.
- `rename` _Bool_ - Whether to just get file name in correct format, or rename file in directory

