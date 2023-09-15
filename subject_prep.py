"""Set up file structure for processing a new patient.

This is the first module to run in the 24/7 preprocessing pipeline. It must be run
before any other module.

Typical usage example:

    patient_prep.py --sid sub-001
"""

from utils import arg_parse
from subject import Subject

def main():
    """Set up file structure."""
    args = arg_parse()
    sid = args.sid

    subject_n = Subject(sid)

    if not subject_n.base_path.exists(): subject_n.create_dir()
    subject_n.transfer_files()
    #TODO: move this to end
    #if not (subject_n.basePath / sid + '-summary.json').exists(): subject_n.create_summary()

if __name__ == "__main__":
    main()