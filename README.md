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

### Documentation for classes:
#### [Subject](markdowns/subject.md)
This class defines a subject.\
Properties of this class are those that relate to 24/7 data on a whole subject level.
#### [ECoG](markdowns/ecog.md)
Properties of this class are those that relate to ECoG data on an individual file level.
#### [Audio](markdowns/audio.md) 
Properties of this class are those that relate to audio data on an individual file level.
#### [Transcript](markdowns/transcript.md) 
#### [Silence](markdowns/silence.md) 
#### [Config](markdowns/config.md) 
