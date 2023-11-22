# 24/7 Preprocessing
See the [Wiki](../../wiki) for information on the project.\
There are 2 main ways to utilize this code.
1. [Standard 24/7 pipeline flow](#main-project)
2. [Implement the data classes in a 24/7 side project](#side-projects)

## Main Project
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

## Side Projects
For projects that use data collected under the 24/7 project, but require different data preparation steps.

## Data Classes 
Both [24/7 Main Project](#main-project) and [24/7 Side Projects](#side-projects) utilize 6 custom classes that help to define and operate on the various types of data and metadata integrated into the pipeline.

### Documentation for classes:
#### [Subject](markdowns/subject.md)
#### [ECoG](markdowns/ecog.md)
#### [Audio](markdowns/audio.md) 
#### [Transcript](markdowns/transcript.md) 
#### [Silence](markdowns/silence.md) 
#### [Config](markdowns/config.md) 
