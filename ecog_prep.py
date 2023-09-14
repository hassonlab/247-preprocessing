"""Prepare ECoG data from new subject.

This is the second module to run in the 24/7 preprocessing pipeline. It must be run
after patient_prep.py and is strongly recommended to be run before audio_prep.py. 
Splits ECoG  data into parts matching audio files, checks for alignment between 
downsampled audio file and audio channel in ECoG data, processes electrode channels.

Typical usage example:

    ecog_prep.py --sid sub-001
"""
import pandas as pd
import datetime as dt
from subject import Subject, Ecog, Audio
from utils import arg_parse
from utils import edf_wav_shift


def edf_wav_alignment(subject_n,ecog_file):
    """Find alignment between ecog and audio data.

    Args:
        subject_n: Information pertaining to subject, DType: patient class object.
        ecog_file: Information and data from one EDF file, DType: ECoG class object.
    """

    # Align with audio
    # TODO: Save audio timestamps with deid audio (?)
    audiotimestamps = pd.read_csv(''.join('/Volumes/hasson/247/subjects/',subject_n.sid,'/audio/',
                                          subject_n.sid,'_timestamps.csv'))
    # NOTE: 798 has 2 mics, 2 audio files listed. This needs to be changed in the audio timestamps code.
    audiotimestamps = audiotimestamps[0::2]
    audiotimestamps = audiotimestamps.reset_index(drop=True)

    subject_n.edf_files[ecog_file.name]['onset'] = str(ecog_file.ecog_hdr['startdate'])
    subject_n.edf_files[ecog_file.name]['offset'] = str(ecog_file.edf_enddatetime)

    for idx in range(0,len(audiotimestamps)):
        aud_startdate = dt.datetime.strptime(audiotimestamps['start date'][idx],'%Y-%m-%d')
        aud_starttime = dt.time.fromisoformat(audiotimestamps[' start time'][idx])
        aud_startdatetime = dt.datetime.combine(aud_startdate,aud_starttime)

        aud_enddate = dt.datetime.strptime(audiotimestamps[' end date'][idx],'%Y-%m-%d')
        aud_endtime = dt.time.fromisoformat(audiotimestamps[' end time'][idx])
        aud_enddatetime = dt.datetime.combine(aud_enddate,aud_endtime)

        if ecog_file.ecog_hdr['startdate'] < aud_startdatetime < ecog_file.edf_enddatetime or ecog_file.ecog_hdr['startdate'] < aud_enddatetime < ecog_file.edf_enddatetime:
            subject_n.edf_files[ecog_file.name]['audio_files'].update({
                        audiotimestamps['File'][idx].split('/')[-1] : {
                            'onset' : str(aud_startdatetime),
                            'offset' : str(aud_enddatetime)
                }
            })

    return subject_n

def get_metadata(subject_n,file):
    """Read header data and calculate EDF end datetime.

    Args:
        subject_n: Information pertaining to subject, DType: patient class object.
        file: Filepath of raw EDF, DType: PosixPath.
    """

    #with (subject_n.inputEDFPath / file).open('rb') as fid:
    ecog_file = Ecog(subject_n.sid,file)
    ecog_file.read_EDFHeader()
    ecog_file.end_datetime() 

    return

def ecog_to_part(subject_n,ecog_file,aud_f):
    """Read data from EDF for specified records.

    Args:
        subject_n: Information pertaining to subject, DType: patient class object.
        ecog_file: Information and data from one EDF file, DType: ECoG class object.
        aud_f: Name of audio file, DType: string.
    """
    aud_startdatetime = dt.datetime.strptime(subject_n.edf_files[ecog_file.name]['audio_files'][aud_f]['onset'],
                                             '%Y-%m-%d %H:%M:%S')
    aud_enddatetime = dt.datetime.strptime(subject_n.edf_files[ecog_file.name]['audio_files'][aud_f]['offset'],
                                           '%Y-%m-%d %H:%M:%S')

    onset_sec = max(int((aud_startdatetime - ecog_file.ecog_hdr['startdate']).total_seconds()),0)
    offset_sec = min(int((aud_enddatetime - ecog_file.ecog_hdr['startdate']).total_seconds()),
                    ecog_file.ecog_hdr['Duration'])

    ecog_file.read_channels(onset_sec,offset_sec)
    return

def quality_check_one(subject_n,ecog_file,aud_f):
    """First quality checks on subject data.

    Args:
        subject_n: Information pertaining to subject, DType: patient class object.
        ecog_file: Information and data from one EDF file, DType: ECoG class object.
        aud_f: Name of audio file, DType: string.
    """
    audio_file = Audio(aud_f)
    audio_file.read_audio(subject_n.audio512Path / aud_f)
    #TODO: modify audio onset/offset in subject_n instance based on hq_lq relsults?
    edf_wav_shift(ecog_file.data,audio_file.audio_track)

def process(ecog_file):
    """Signal processing on EDF file."""
    return

def write_edf_part(subject_n,ecog_file):
    ecog_file.write_edf()
    return

def main():
    """Prepare ECoG data for a subject."""
    
    args = arg_parse()
    sid = args.sid
    input_name = args.input_name

    subject_n = Subject(sid)
    subject_n.update_log('02_ecog_prep: start')
    subject_n.edf_list()
    #mypath = Path('/Users/baubrey/Documents/pipeline/subjects/' + sid + header.input_subpath)

    for file in subject_n.edf_files:
        # Read original EDF
        ecog_file = get_metadata(subject_n,file)
        subject_n = edf_wav_alignment(subject_n,ecog_file)
        
        for aud_f in subject_n.edf_files[ecog_file.name]['audio_files']:
            ecog_to_part(subject_n,ecog_file,aud_f)
            # TODO: the header also needs to be updated with a new duration

            # TEMP naming conversion... this will be the name of aud_f in the future
            part_num = aud_f.split('_')[1]
            aud_f = sid + '_Part' + part_num + '_audio512Hz.wav'

            quality_check_one(subject_n,ecog_file,aud_f)
            ecog_file.process_ecog()
            ecog_file.name = ''.join([ecog_file.sid,'_ecog-raw_',aud_f.split('_')[1],'.edf'])
            write_edf_part(subject_n,ecog_file)

    subject_n.update_log('02_ecog_prep: end')

    return

if __name__ == "__main__":
    main()