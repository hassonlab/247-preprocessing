<a id="subject"></a>

# subject

Class: subject and Subclasse: ecog, audio, and transcript definitions.

...

Typical usage example:

  subject_n = subject()
  subject_n.create_dir()

<a id="subject.Subject"></a>

## Subject Objects

```python
class Subject()
```

Information about a patient.

Aggregates information about data collected for a given patient.

**Attributes**:

- `sid` - The unique subject indentifier, DType: string.
- `base_path` - Subject base directory, DType: Posix path.
- `audio_512_path` - Subject downsampled audio directory, DType: Posix path.
- `audio_deid_path` - Subject de-identified audio directory, DType: Posix path.
- `ecog_raw_path` - Subject raw EDF directory, DType: Posix path.
- `ecog_processed_path` - Subject processed EDF directory, DType: Posix path.

<a id="subject.Subject.__init__"></a>

#### \_\_init\_\_

```python
def __init__(sid: str, create_config=False)
```

Initializes the instance based on subject identifier.

**Arguments**:

- `sid` - Identifies subject, Dtype: string.

<a id="subject.Subject.update_log"></a>

#### update\_log

```python
def update_log(message: str)
```

Update logger for each step in the pipeline.

**Arguments**:

- `message` - message written to log file, DType: string.

<a id="subject.Subject.audio_list"></a>

#### audio\_list

```python
def audio_list()
```

Retruns list of audio files present in subject directory.

<a id="subject.Subject.edf_list"></a>

#### edf\_list

```python
def edf_list()
```

Retruns list of EDF files present in subject directory.

<a id="subject.Subject.transcript_list"></a>

#### transcript\_list

```python
def transcript_list()
```

Retruns list of xml transcript files present in subject directory.

<a id="subject.Subject.make_edf_wav_dict"></a>

#### make\_edf\_wav\_dict

```python
def make_edf_wav_dict()
```

Start a dictionary for alignment between EDF and WAV files.

<a id="subject.Subject.create_subject_transcript"></a>

#### create\_subject\_transcript

```python
def create_subject_transcript()
```

Create an empty, subject-level transcript that will be filled with each part-level transcript.

<a id="subject.Subject.create_summary"></a>

#### create\_summary

```python
def create_summary()
```

Create summary file for new patient, written to throughout pipeline.

<a id="subject.Subject.create_dir"></a>

#### create\_dir

```python
def create_dir()
```

Create directory and standard sub-directories for a new subject.

<a id="subject.Subject.transfer_files"></a>

#### transfer\_files

```python
def transfer_files(filetypes: list = ["ecog", "audio-512Hz", "audio-deid"])
```

Transfer files to patient directory.

Connect to Globus Transfer API and transfer files from NYU endpoint
to Princeton endpoint.

**Arguments**:

- `filetypes` - Which files to transfer, Dtype: list.

<a id="subject.Subject.rename_files"></a>

#### rename\_files

```python
def rename_files(newpath, file: Path, part: str, type: str, rename=False)
```

Rename and/or move files.

...

**Attributes**:

- `part` - file identifier, DType: str.
- `file` - file path, DType: PosixPath.
- `type` - label indicating file type: DType: str.
- `ext` - file extension: DType: str.

