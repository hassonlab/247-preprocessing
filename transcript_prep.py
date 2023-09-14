"""Generate patient transcript.

This is the fourth module to run in the 24/7 preprocessing pipeline. It must be run
after patient_prep.py and audio_prep.py, and is strongly recommended to be run after 
ecog_prep.py. Aggregates part transcripts into patient transcript, converts timings to 
datetimes, aggregates de-id labels.

Typical usage example:

    transcript_prep.py --sid sub-001
"""
import glob
from utils import arg_parse
from subject import subject, transcript

def main():
    """Generate patient transcript."""

    args = arg_parse()
    sid = args.sid
    input_name = args.input_name

    subject_n = subject(sid)
    subject_n.update_log('04_transcript_prep: start')
    subject_n.transcript_list()

    for file in subject_n.xml_files:
        partTranscript = transcript(sid,file)
        partTranscript.parse_xml()

    subject_n.update_log('04_transcript_prep: end')

    return

if __name__ == "__main__":
    main()