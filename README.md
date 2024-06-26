# 24/7 Preprocessing
See the [Wiki](../../wiki) for information on the project.\
There are 2 main ways to utilize this code.
1. [Standard 24/7 pipeline flow](#main-project)
2. [Implement the data classes in a 24/7 side project](#side-projects)

## Main Project
Prepare data collected under the 24/7 project for analysis.

### Getting Started
1. Clone the repository:  
`git clone https://github.com/hassonlab/247-preprocessing.git`
2. Create your conda environment with required packages:  
`conda env create -f environment.yml`
### Usage
`python pipeline_247.py --sid sub-###`
#### Step 00: Data collection
...
#### Step 01: Transfer preparation
...
#### Step 02: Subject preparation
`python pipeline_247.py --sid sub-### --steps subject_prep`
#### Step 03: ECoG preparation
Run for every subject EDF file:\
`python pipeline_247.py --sid sub-### --steps ecog_prep`

#### Step 04: Audio preparation
Run for every subject de-identified audio file:\
`python pipeline_247.py --sid sub-### --steps audio_prep`

#### Step 05: Transcript preparation
Run for every subject transcript file:\
`python pipeline_247.py --sid sub-### --steps transcript_prep`

#### Step 06: Subject summarization
...

## Related Projects
For projects that use data collected under the 24/7 project, but require different data preparation steps.

## Data Classes 
Both [24/7 Main Project](#main-project) and [24/7 Affiliate Projects](#side-projects) utilize 6 custom classes that help to define and operate on the various types of data and metadata integrated into the pipeline.

### Documentation for classes:
#### [Subject](docs/subject.md)
#### [ECoG](docs/ecog.md)
#### [Audio](docs/audio.md) 
#### [Transcript](docs/transcript.md) 
#### [Silence](docs/silence.md) 
#### [Config](docs/config.md) 
