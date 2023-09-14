"""Class: subject and Subclasse: ecog, audio, and transcript definitions.

...

Typical usage example:

  subject_n = subject()
  subject_n.create_dir()
"""

import socket
import json
import logging
import getpass
import subprocess
import pyedflib
import warnings
import taglib
import inflect
import re
import numpy as np
import datetime as dt
import pandas as pd
import xml.etree.ElementTree as ET
from pathlib import Path
from pydub import AudioSegment
#import tracemalloc
#import timeit
#from scipy.io import wavfile
#from pydub.playback import play
#from pydub.utils import mediainfo
#from collections import deque
#import globus_sdk
#from globus_sdk.scopes import TransferScopes

class Subject:
    """Information about a patient.

    Aggregates information about data collected for a given patient.

    Attributes:
        sid: The unique subject indentifier, DType: string.
        basePath: Subject base directory, DType: Posix path.
        audio512Path: Subject downsampled audio directory, DType: Posix path.
        audioDeidPath: Subject de-identified audio directory, DType: Posix path.
        rawEDFPath: Subject raw EDF directory, DType: Posix path.
        processedEDFPath: Subject processed EDF directory, DType: Posix path.
    """

    def __init__(self,sid):
        """Initializes the instance based on subject identifier.

        Args:
          sid: Identifies subject, Dtype: string.
        """
        self.sid = sid

        host = socket.gethostname()

        if host == 'scotty.pni.Princeton.EDU':
            self.basePath = Path('/mnt/cup/labs/hasson/247/subjects/' + self.sid)
        else:
            self.basePath = Path('/Volumes/hasson/247/subjects/' + self.sid)
                
        #self.basePath = Path('/Users/baubrey/Documents/pipeline/subjects/' + self.sid)
        self.audio512Path = self.basePath / 'audio/audio-512Hz/'
        self.audioDeidPath = self.basePath / 'audio/audio-deid/'
        self.audioTranscribePath = self.basePath / 'audio/audio-transcribe/'
        self.rawEDFPath = self.basePath / 'ecog/ecog-raw/'
        self.processedEDFPath = self.basePath / 'ecog/ecog-processed/'
        self.silencePath = self.basePath / 'notes/de-id/'
        self.transcriptPath = self.basePath / 'transcript/'


    def update_log(self,message):
        """Update logger for each step in the pipeline.

        Args:
          message: message written to log file, DType: string.
        """
        logging.basicConfig(filename=(self.basePath / 'log/example.log'), 
                        level=logging.INFO, format='%(asctime)s %(message)s')
        logging.info(message + ", User: %s",getpass.getuser())

        #start = timeit.default_timer()
        #tracemalloc.start()
        #current = tracemalloc.get_traced_memory()
        #print(current)
        #tracemalloc.stop()
        #stop = timeit.default_timer()

        #print('Time: ', stop - start) 

    
    def audio_list(self):
        """Retruns list of audio files present in subject directory."""
        aud512_files = [f for f in self.audio512Path.rglob('[!.]*') if f.is_file()]
        self.aud512_files = aud512_files

        audDeid_files = [f.name for f in self.audioDeidPath.rglob('[!.]*') if f.is_file()]
        self.audDeid_files = audDeid_files

                
    def edf_list(self):
        """Retruns list of EDF files present in subject directory."""

        edf_files = [f.name for f in self.rawEDFPath.iterdir() if f.is_file()]
        self.rawEDFPath = self.rawEDFPath
        self.edf_files = { k: { 'onset': {},'offset': {},'audio_files':{} } for k in edf_files }


    def transcript_list(self):
        """Retruns list of xml transcript files present in subject directory."""
        xml_files = [f for f in (self.transcriptPath / 'xml/').rglob('[!.]*') if f.is_file()]
        self.xml_files = xml_files


    def create_summary(self):
        """Create summary file for new patient, written to throughout pipeline."""
        with open(self.basePath / self.sid + '-summary.json', 'w', encoding='utf-8') as f:
            json.dump(edf_wav_dict, f, ensure_ascii=False, indent=4)
    

    def create_dir(self):
        """Create directory and standard sub-directories for a new subject."""
        self.audio512Path.mkdir(parents=True)
        self.audioDeidPath.mkdir(parents=True)
        self.audioTranscribePath.mkdir(parents=True)
        self.rawEDFPath.mkdir(parents=True)
        self.processedEDFPath.mkdir(parents=True)
        (self.basePath / 'anat').mkdir(parents=True)
        (self.basePath / 'issue').mkdir(parents=True)
        (self.basePath / 'notes').mkdir(parents=True)
        (self.basePath / 'transcript/xml').mkdir(parents=True)

    
    def transfer_files(self,filetypes):
        """Transfer files to patient directory.
        
        Connect to Globus Transfer API and transfer files from NYU endpoint 
        to Princeton endpoint.

        Args:
          filetypes: Which files to transfer, Dtype: list.
        """
        # We use Globus Transfer API to transfer large EDF files
        # Using Globus-CLI works, but there's probably a better way to do this

        source_endpoint_id = "28e1658e-6ce6-11e9-bf46-0e4a062367b8:"
        dest_endpoint_id = "6ce834d6-ff8a-11e6-bad1-22000b9a448b:"

        #TODO: fix this
        for filetype in filetypes:
            if filetype == 'audio-512Hz':
                source_path = 'NY'.join([self.sid,"ZoomAudioFilesDownsampled/"])
                dest_path = str(self.basePath / 'audio/audio-512Hz/')
            elif filetype == 'ecog':
                source_path = 'NY'.join([self.sid,"Dayfiles/"])
                dest_path = str(self.basePath / 'ecog/ecog-raw/')
            elif filetype == 'audio-deid':
                source_path = 'NY'.join([self.sid,"ZoomAudioFilesDeid/"])
                dest_path = str(self.basePath / 'audio/audio-deid/')

            globus_cmd = ' '.join(['globus', 'login;',
                        'globus', 'transfer', source_endpoint_id + source_path, dest_endpoint_id + dest_path])
        subprocess.run(globus_cmd,shell=True)

        # TODO: rename files


class Ecog(Subject):
    """Information and data for each patient ECoG file.

    ...

    Attributes:
        sid: A string indicating the unique subject indentifier.
        file: Name of edf file, DType: string.
        basePath: A pathlib PosixPath object pointing to the subject base directory.
        audio512Path: A pathlib PosixPath object pointing to the subject downsampled audio directory.
        audioDeidPath: A pathlib PosixPath object pointing to the subject de-identified audio directory.
        rawEDFPath: A pathlib PosixPath object pointing to the subject raw EDF directory.
        processedEDFPath: Subject processed EDF directory, DType: Posix path.
        nonElectrodeId: A list of strings indicating which channel labels are not electrodes.
        expected_sr: Integer of expected sampling rate.
        name: A string of the EDF file name.

        ecog_hdr: EDF header data, DType: dict.
        sampRate: Sampling rate of electrode channels, DType: int.
        edf_enddatetime: End date time of EDF file, DYype: datetime.
        data: EDF channel data, DType: numpy array. (?)
    """
        
    def __init__(self,sid,file):
        """Initializes the instance based on subject identifier and file identifier.

        Args:
          sid: Identifies subject, DType: string.
        """

        # Inherit __init__ from patient super class (file directories).       
        Subject.__init__(self,sid)
        self.name = file
        self.nonElectrodeId = ['SG','EKG','DC']
    
    expected_sr = 512
    #warnings.simplefilter("ignore")

    def read_EDFHeader(self):
        """Read EDF header."""
        self.ecog_hdr = pyedflib.highlevel.read_edf_header(str(self.rawEDFPath / self.name), 
                                                           read_annotations=True)
        self.sampRate = int(self.ecog_hdr['SignalHeaders'][0]['sample_rate'])

    
    def end_datetime(self):
        """Calculate EDF end datetime from start datetime and file duration."""
        #edf_dur_seconds = self.nRecords*self.recDurSec
        edf_duration = dt.timedelta(seconds=self.ecog_hdr['Duration'])
        self.edf_enddatetime = self.ecog_hdr['startdate'] + edf_duration

    
    def read_channels(self,onset_sec,offset_sec):
        """Read EDF channels for a certain time frame.
        
        Args:
            onset_sec: Beginning of time frame to read, DType: int.
            offset_sec: End of time frame to read, DType: int.
        """
        # test value
        offset_sec = 60
        nChans = range(200,len(self.ecog_hdr['channels']))
        nSamps = offset_sec*self.sampRate - onset_sec*self.sampRate
        data = np.empty([len(self.ecog_hdr['channels']),nSamps])
        ecog_data = pyedflib.EdfReader(str(self.rawEDFPath / self.name))
        for chan in nChans:
            data[chan] = ecog_data.readSignal(chan, onset_sec, offset_sec*self.sampRate)
        self.data = data
        ecog_data.close()

    
    def process_ecog(self):
        """Process signal data."""
        return

    def write_edf(self):
        """Write EDF file."""

        sigHdrs = self.ecog_hdr['SignalHeaders']
        del self.ecog_hdr['SignalHeaders']
        #phys min and max are swapped for some reason
        for idx,hdr in enumerate(sigHdrs):
            if hdr['physical_min'] > hdr['physical_max']:
                sigHdrs[idx]['physical_min'] = -(hdr['physical_min'])
                sigHdrs[idx]['physical_max'] = -(hdr['physical_max'])

        # Suppress warnings from edfwriter
        warnings.filterwarnings(action='ignore',category=UserWarning,module=r'.*edfwriter')
        
        # Temp name (?) with datetime
        outname = str(self.processedEDFPath / self.name)
        pyedflib.highlevel.write_edf(outname, self.data, sigHdrs, header=self.ecog_hdr)

    
class Audio(Subject):
    """Information and data for each patient audio file.

    ...

    Attributes:
        sid: Unique subject indentifier, DType: str.
        name: Name of audio file, DType: str.
        basePath: Subject base directory, DType: PosixPath.
        audioDeidPath: Subject de-identified audio directory, DType: PosixPath.
        audioTranscribePath: Subject transcription audio directory, DType: PosixPath.
        deidAudio: Data from de-identified audio file (input audio), DType: Pydub AudioSegment.
        transcribeAudio: Audio data for transcription (output audio), DType: Pydub AudioSegment.
    """
        
    def __init__(self,sid,file):
        """Initializes the instance based on file identifier.

        Args:
          fid: File identifier.
        """
        # Inherit __init__ from patient super class.       
        Subject.__init__(self,sid)
        self.name = file

            
    def read_audio(self):
        """Read audio signal.

        Args:
          filepath: Path to audio file.
        """
        #TODO: option for reading multiple tracks?
        self.deidAudio = AudioSegment.from_wav(self.audioDeidPath / self.name)
        #play(audioPart)
        # NOTE: pydub does things in milliseconds


    def crop_audio(self,silenceFile):
        """Remove marked segments from audio. For uploading for transcription."""
        # TODO: The deid audio files might be split parts
        # TODO: Do more checks 
        silences = pd.read_csv(silenceFile,header=None,
                               names=['onset_min','onset_sec','offset_min','offset_sec','silence_type'])
        
        # Change silence times to milliseconds
        silence_onsets = []
        silence_offsets = []
        for _, row in silences.iterrows():
            onset_ms = 1000*((row.onset_min*60)+row.onset_sec)
            offset_ms = 1000*((row.offset_min*60)+row.offset_sec)
            silence_onsets.append(onset_ms)
            silence_offsets.append(offset_ms)

        # Get speech times from silence times
        speech_onsets = np.array(silence_offsets)
        speech_offsets = np.roll(silence_onsets,-1)

        # Remove consecutive non-speech labels
        speech_idxs = np.where((speech_offsets-speech_onsets) != 0)
        speech_times = zip(speech_onsets[speech_idxs],speech_offsets[speech_idxs])
        # Concat segments
        crop_audio = AudioSegment.empty()
        for time in speech_times:
            crop_audio += self.deidAudio[time[0]:time[1]]
        self.transcribeAudio = crop_audio

    def slow_audio(self):
        """Slow down audio for transcription."""

        #slow_speed = 0.95
        #y_slow = librosa.effects.time_stretch(y, rate=slow_speed)
        sfaud = self.transcribeAudio._spawn(self.transcribeAudio.raw_data, overrides={
        "frame_rate": int(self.transcribeAudio.frame_rate * 0.95)
        }).set_frame_rate(self.transcribeAudio.frame_rate)
        #sfaud = sound_with_altered_frame_rate.set_frame_rate(self.audioTrack.frame_rate)
        #breakpoint()
        self.transcribeAudio = sfaud

    def write_audio(self):
        """Write audio signal."""
        self.transcribeAudio.export(self.audioTranscribePath / self.name, format='wav')
        with taglib.File(self.audioDeidPath / self.name, save_on_exit=True) as audioFile:
            audioFile.tags['startDateTime'] = 'startDateTime'
            audioFile.tags['endDateTime'] = 'endDateTime'
            
    
class Transcript(Subject):
    """Transcript corresponding to a specific audio file.

    ...

    Attributes:
        fid: A pathlib PosixPath object pointing to the transcript.
    """

    def __init__(self,sid,file):
        # Inherit __init__ from patient super class.       
        Subject.__init__(self,sid)
        self.name = file


    def parse_xml(self):
        """Convert Verbit.AI format to our format."""
        #transcript_df = pd.DataFrame(columns=['token_idx', 'token_type', 'token', 'onset_day', 'onset_time', 
        #                                      'offset_day', 'offset_time', 'utterance_idx', 'audio_file'])
        transcipt = []
        utterance_idx = 0
        # get element tree
        tree = ET.parse(self.transcriptPath / 'xml/' / self.name) 
        # get root
        root = tree.getroot()
        # loop through and index into relevant children
        for child in root.findall('.//{http://www.w3.org/2006/10/ttaf1}div/{http://www.w3.org/2006/10/ttaf1}p'):
            text = child.text
            onset = child.attrib['begin']
            offset = child.attrib['end']
            line = text.split(' ')
            if line[0] == '>>': 
                utterance_idx += 1
                del line[0]
            for elem in line:
                token = re.split('.,!?',elem)
                if '[' in elem: token_type = 'tag'
                line_list = [token_type, token, onset, offset, utterance_idx]
                breakpoint()

        return

    def add_dt(self):
        """Add audio date-time inofrmation."""
        # From audio header

        return

    def agg_datum(self):
        """Aggregate part-level transcription into full patient datum."""

        return