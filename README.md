# 24/7 Preprocessing

## Standard 24/7 Pipeline Flow
Prepare data collected under the 24/7 project for analysis.

### Getting Started
`git clone https://github.com/hassonlab/247-preprocessing.git`
### Usage
#### Step 00: Data collection
...
#### Step 01: Transfer preparation
...
#### Step 02: Subject preparation
` python subject_prep.py --sid sub-001 `
#### Step 03: ECoG preparation
Run for every subject EDF file:\
` python ecog_prep.py --sid sub-001 `

Run for a specific file:\
` python ecog_prep.py --sid sub-001 --fid NAME.EDF `
#### Step 04: Audio preparation
Run for every subject de-identified audio file:\
` python audio_prep.py --sid sub-001 `

Run for a specific file:\
` python audio_prep.py --sid sub-001 --fid 001 `
#### Step 05: Transcript preparation
Run for every subject transcript file:\
` python transcript_prep.py --sid sub-001 `

Run for a specific file:\
` python transcript_prep.py --sid sub-001 --fid 001 `
#### Step 06: Subject summarization
...

## Data Classes 
The pipeline utilizes 5 custom classes that help to define and operate on the various types of data and metadata integrated into the pipeline.

### Class: Subject 
This class defines a subject.\
Properties of this class are those that relate to 24/7 data on a whole subject level.\
` subject.create_dir() `: Create new directory for the processing of a new subject, and all associated child directories.\
` subject.transfer_files() `: Interact with Globus Transfer API to transfer files from endpoint to endpoint.\
` subject.rename_files() `: Enforce naming convention on files.\
` subject.audio_list() `: Returns a list of all audio files in subject directory.\
` subject.edf_list() `: Returns a list of all EDF files in subject directory.\
` subject.transcript_list() `: Returns a list of all transcript files in subject directory.\
` subject.make_edf_wav_dict() `: Create a dictionary that provides information about corresponding ECoG and audio files.\
` subject.create_subject_transcript() `: Create empty pandas DataFrame with columns for transcripts (Prob link to Wiki to define columns/what they're for).\
` subject.update_log() `: Update subject log file.\
In the standard pipeline, Step 02: Subject Preparation initiates a new instance of the class Subject.

### Class: ECoG
[ecog class](markdowns/ecog.md)
