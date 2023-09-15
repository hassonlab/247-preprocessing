# 24/7 Preprocessing
Prepare data collected under the 24/7 project for analysis.

## Getting Started
`git clone https://github.com/hassonlab/247-preprocessing.git`
## Usage
### Step 00: Data collection
...
### Step 01: Transfer preparation
...
### Step 02: Subject preparation
` python subject_prep.py --sid sub-001 `
### Step 03: ECoG preparation
Run for every subject EDF file:\
` python ecog_prep.py --sid sub-001 `

Run for a specific file:\
` python ecog_prep.py --sid sub-001 --fid NAME.EDF `
### Step 04: Audio preparation
Run for every subject de-identified audio file:\
` python audio_prep.py --sid sub-001 `

Run for a specific file:\
` python audio_prep.py --sid sub-001 --fid 001 `
### Step 05: Transcript preparation
Run for every subject transcript file:\
` python transcript_prep.py --sid sub-001 `

Run for a specific file:\
` python transcript_prep.py --sid sub-001 --fid 001 `
### Step 06: Subject summarization
...
