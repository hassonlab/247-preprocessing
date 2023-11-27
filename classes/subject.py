import json
import logging
import getpass
import subprocess
import pandas as pd
from pathlib import Path

# import tracemalloc
# import timeit
# from scipy.io import wavfile
# from pydub.playback import play
# from pydub.utils import mediainfo
# from collections import deque
# import globus_sdk
# from globus_sdk.scopes import TransferScopes

# TODO: need more consistency in using path + file name vs. just file name in classes


class Subject:
    """Setup for a new patient.

    Aggregates information about data collected for a given patient.

    Attributes:
        sid (str): The unique subject indentifier.
        base_path (PosixPath): Subject base directory.
        audio_512_path (PosixPath): Subject downsampled audio directory.
        audio_deid_path (PosixPath): Subject de-identified audio directory.
        ecog_raw_path (PosixPath): Subject raw EDF directory.
        ecog_processed_path (PosixPath): Subject processed EDF directory.
    """

    def __init__(self, sid: str, create_config=False):
        """Initializes the instance based on subject identifier.

        Args:
          sid (str): Identifies subject.
        """
        self.sid = sid
        self.base_path = Path.cwd().parents[1] / "subjects" / self.sid

        # host = socket.gethostname()

        # if host == "scotty.pni.Princeton.EDU":
        #     self.base_path = Path(self.scotty_prefix_path) / self.base_path / self.sid
        # else:
        #     self.base_path = Path(self.user_prefix_path) / self.base_path / self.sid

    def update_log(self, message: str):
        """Update logger for each step in the pipeline.

        Args:
          message: message written to log file, DType: string.
        """
        logging.basicConfig(
            filename=(self.filenames["log"] / "example.log"),
            level=logging.INFO,
            format="%(asctime)s %(message)s",
        )
        logging.info(message + ", User: %s", getpass.getuser())

        # start = timeit.default_timer()
        # tracemalloc.start()
        # current = tracemalloc.get_traced_memory()
        # print(current)
        # tracemalloc.stop()
        # stop = timeit.default_timer()

        # print('Time: ', stop - start)

    def audio_list(self):
        """Retruns list of audio files present in subject directory."""
        audio_512_files = [
            f
            for f in self.filenames["audio_downsampled"].parent.rglob("[!.]*")
            if f.is_file()
        ]
        self.audio_512_files = audio_512_files

        audio_deid_files = [
            f for f in self.filenames["audio_deid"].parent.rglob("[!.]*") if f.is_file()
        ]
        self.audio_deid_files = audio_deid_files

    def edf_list(self):
        """Retruns list of EDF files present in subject directory."""
        # TODO: I don't know if this is consistant across subject (on nyu server)
        self.edf_files = [
            f for f in self.filenames["ecog_raw"].parent.rglob("[!.]*") if f.is_file()
        ]

    def transcript_list(self):
        """Retruns list of xml transcript files present in subject directory."""
        xml_files = [
            f for f in self.filenames["transcript"].rglob("[!.]*") if f.is_file()
        ]
        self.xml_files = xml_files

    def make_edf_wav_dict(self):
        """Start a dictionary for alignment between EDF and WAV files."""
        self.alignment = {
            k.name: {"onset": {}, "offset": {}, "audio_files": {}}
            for k in self.edf_files
        }

    def create_subject_transcript(self):
        """Create an empty, subject-level transcript that will be filled with each part-level transcript."""
        self.transcript = pd.DataFrame(
            columns=[
                "token_type",
                "token",
                "onset",
                "offset",
                "speaker",
                "utterance_idx",
            ]
        )

    def create_summary(self):
        """Create summary file for new patient, written to throughout pipeline."""
        with open(
            self.base_path / self.sid + "-summary.json", "w", encoding="utf-8"
        ) as f:
            json.dump(edf_wav_dict, f, ensure_ascii=False, indent=4)

    def create_dir(self):
        """Create directory and standard sub-directories for a new subject."""
        for path in self.filenames:
            if self.filenames[path].suffix:
                self.filenames[path].parent.mkdir(parents=True)
            elif not self.filenames[path].suffix:
                self.filenames[path].mkdir(parents=True)

    def transfer_files(self, filetypes: list = ["ecog", "audio-512Hz", "audio-deid"]):
        """Transfer files to patient directory.

        Connect to Globus Transfer API and transfer files from NYU endpoint
        to Princeton endpoint.

        Args:
          filetypes (list): Which files to transfer.
        """
        # We use Globus Transfer API to transfer large EDF files
        # Using Globus-CLI works, but there's probably a better way to do this

        # TODO: not waiting for activation?
        globus_cmd = " ".join(
            [
                "globus",
                "login;",
                "globus",
                "endpoint",
                "activate",
                "--web",
                self.dest_endpoint_id,
            ]
        )
        subprocess.run(globus_cmd, shell=True)

        for filetype in filetypes:
            if filetype == "audio-512Hz":
                source_path = self.nyu_downsampled_audio_path
                dest_path = self.filenames["audio_downsampled"].parent
            elif filetype == "audio-deid":
                source_path = self.nyu_deid_audio_path
                dest_path = self.filenames["audio_deid"].parent
            elif filetype == "ecog":
                source_path = self.nyu_ecog_path
                dest_path = self.filenamess["ecog_raw"].parent

            source = self.source_endpoint_id + ":" + str(source_path)
            dest = self.dest_endpoint_id + ":" + str(dest_path)

            transfer_cmd = " ".join(
                [
                    "globus",
                    "transfer",
                    "-r",
                    source,
                    dest,
                    "--jmespath",
                    "task_id",
                    "--format=UNIX",
                ]
            )

            tsk = (
                subprocess.check_output(transfer_cmd, shell=True)
                .decode("utf-8")
                .replace("\n", "")
            )

            # TODO: instead of waiting for each one, should submit all then wait
            wait_cmd = " ".join(["globus", "task", "wait", tsk])
            subprocess.run(wait_cmd, shell=True)

    def rename_files(self, newpath: Path, file: Path, part: str, type: str, rename=False):
        """Rename and/or move files.

        ...

        Attributes:
            newpath (PosixPath): new path
            part (str): file identifier.
            file (PosixPath): file path.
            part (str): file part
            type (str): label indicating file type.
            ext (str): file extension.
            rename (Bool): Whether to just get file name in correct format, or rename file in directory
        """
        # Ecog and downsampled audio files are not transferred with correct names
        # TODO: What do we want to do with multiple audio tracks?
        # TODO: Re-evaluate this function

        file_name = self.filenames[type].name.format(sid=self.sid, part=part)
        # rename files and move directory
        if rename == True:
            file.rename(newpath / file_name)

        return file_name
