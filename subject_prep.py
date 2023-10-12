"""Set up file structure for processing a new patient.

This is the first module to run in the 24/7 preprocessing pipeline. It must be run
before any other module.

Typical usage example:

    patient_prep.py --sid sub-001
"""

import time
from utils import arg_parse
from subject import Subject, Config
from pathlib import Path


def main():
    """Set up file structure."""
    args = arg_parse()
    nyu_id = args.nyu_id
    new_id = args.sid

    config = Config(new_id, nyu_id)
    config.configure_paths()
    config.configure_paths_nyu()

    subject_n = Subject(new_id, create_config=True)
    subject_n.filenames = config.filenames
    subject_n.__dict__.update(config.nyu_paths.items())

    if not config.base_path.exists():
        subject_n.create_dir()

    config.write_config()
    subject_n.update_log("01_patient_prep: start")

    # subject_n.transfer_files()

    subject_n.edf_list()
    # TODO: naming
    for part, file in enumerate(sorted(subject_n.edf_files)):
        subject_n.rename_files(
            file.parents[1], file, str(part + 1).zfill(3), "ecog_raw", rename=True
        )
        # At this point, the directory should be empty and can be removed
        while file.exists():
            time.sleep(1)
        file.parents[0].rmdir()

    # NOTE: We can get the correct naming when we run downsampling/deid on nyu server
    subject_n.audio_list()
    for part, file in enumerate(sorted(subject_n.audio_512_files)):
        subject_n.rename_files(
            file.parents[1],
            file,
            str(part + 1).zfill(3),
            "audio_downsampled",
            rename=True,
        )

        # TODO: needs more testing
        while any(file.parents[0].iterdir()):
            time.sleep(1)
        file.parents[0].rmdir()

    for part, file in enumerate(sorted(subject_n.audio_deid_files)):
        subject_n.rename_files(
            file.parents[0], file, str(part + 1).zfill(3), "audio_deid", rename=True
        )

    subject_n.update_log("01_patient_prep: end")

    # TODO: move this to end
    # if not (subject_n.basePath / sid + '-summary.json').exists(): subject_n.create_summary()


if __name__ == "__main__":
    main()
