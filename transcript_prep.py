"""Generate patient transcript.

This is the fourth module to run in the 24/7 preprocessing pipeline. It must be run
after patient_prep.py and audio_prep.py, and is strongly recommended to be run after 
ecog_prep.py. Aggregates part transcripts into patient transcript, converts timings to 
datetimes, aggregates de-id labels.

Typical usage example:

    transcript_prep.py --sid sub-001
"""
import pandas as pd
from utils import arg_parse
from subject import Subject, Transcript


def get_audio_onset(subject_n, transcript_file):
    # TODO: TEMP
    audiotimestamps = pd.read_csv(''.join([
        '/Volumes/hasson/247/subjects/', transcript_file.sid, '/audio/',
        transcript_file.sid, '_timestamps.csv'
    ]))
    # NOTE: 798 has 2 mics, 2 audio files listed. This needs to be changed in the audio timestamps code.
    audiotimestamps = audiotimestamps[0::2]
    audiotimestamps = audiotimestamps.sort_values(
        by=['start date', ' start time'])
    audiotimestamps = audiotimestamps.reset_index(drop=True)
    part_num = int(transcript_file.name.split('_')[1][-3:])
    onset_day = audiotimestamps['start date'][part_num]
    onset_time = audiotimestamps[' start time'][part_num]

    transcript_file.add_dt(onset_day, onset_time)

    partname = str(transcript_file.name).split('_')
    silence_file = subject_n.silence_path / ''.join(
        [partname[0], '_', partname[1], '_silences.csv'])
    transcript_file.agg_silences(silence_file)
    return


def main():
    """Generate patient transcript."""

    args = arg_parse()
    sid = args.sid
    input_name = args.input_name

    subject_n = Subject(sid)
    subject_n.update_log('04_transcript_prep: start')
    subject_n.transcript_list()
    subject_n.create_subject_transcript()

    for file in subject_n.xml_files:
        transcript_file = Transcript(sid, file.name)
        transcript_file.parse_xml()
        transcript_file.convert_timedelta()
        transcript_file.compress_transcript(0.05)
        get_audio_onset(subject_n, transcript_file)
        subject_n.transcript = subject_n.transcript.append(
            transcript_file.transcript)

    subject_n.transcript = subject_n.transcript.rename_axis(
        'part_idx').sort_values(by=['onset', 'part_idx']).reset_index()
    subject_n.transcript.to_csv(subject_n.transcript_path /
                                '_'.join([subject_n.sid, 'transcript.csv']))

    subject_n.update_log('04_transcript_prep: end')

    return


if __name__ == "__main__":
    main()
