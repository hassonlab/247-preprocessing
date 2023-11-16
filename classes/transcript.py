import re
import pandas as pd
import xml.etree.ElementTree as ET


class Transcript:
    """Transcript corresponding to a specific audio file.

    ...

    Attributes:
        file (PosixPath): Path to the transcript.
    """

    def __init__(self, sid: str, file):
        """Initializes the instance based on file identifier.

        Args:
          file (PosixPath): Path to the transcript.
        """
        # Inherit __init__ from patient super class.
        # Subject.__init__(self, sid)
        self.file = file

    def parse_xml(self):
        """Convert Verbit.AI format to our format."""
        # Empty list to append to
        transcript = []
        # Increase utterance count for every new utterance
        utterance_idx = -1
        # Punctuation we want to split and maintain from tokens
        punc = "([. |, |! |?])"
        # get element tree
        tree = ET.parse(self.file)
        root = tree.getroot()

        # Speaker will be 'Unknown' if the first line doesn't contain a speaker label,
        # else speaker label is maintained from previous line.
        speaker = "Unknown"
        # loop through and index into relevant children
        for child in root.findall(
            ".//{http://www.w3.org/2006/10/ttaf1}div/{http://www.w3.org/2006/10/ttaf1}p"
        ):
            text = child.text
            onset = child.attrib["begin"]
            offset = child.attrib["end"]

            # This is an empy line. It might be the case that the next line has both words (?)
            if text == None:
                continue

            if "[" in text:
                # Remove whitespace inside square brackets so we don't split a single tag
                start_idx = text.index("[")
                end_idx = text.index("]") + 1
                text = (
                    text[:start_idx]
                    + text[start_idx:end_idx].replace(" ", "")
                    + text[end_idx:]
                )

            # Split if multiple tokens in line
            line = text.split(" ")

            # '>>' indicates new utterance
            if line[0] == ">>":
                utterance_idx += 1
                del line[0]

                # Update speaker
                label_break = [idx for idx, s in enumerate(line) if ":" in s]
                if label_break:
                    speaker = "".join(line[: label_break[0] + 1]).replace(":", "")
                    del line[: label_break[0] + 1]
            for elem in line:
                # Split if contains punctuation
                tokens = re.split(punc, elem)
                for token in tokens:
                    # Square brackets indicates tag
                    if "[" in token:
                        token_type = "tag"
                    elif token in punc:
                        token_type = "punctuation"
                        # TODO: Does the punctuation we want always come at the end of line?
                        del tokens[-1]
                    else:
                        token_type = "word"
                    # List for this line
                    line_list = [
                        token_type,
                        token,
                        onset,
                        offset,
                        speaker,
                        utterance_idx,
                    ]
                    # Append to full part transcript
                    transcript.append(line_list)

        self.transcript = pd.DataFrame(
            transcript,
            columns=[
                "token_type",
                "token",
                "onset",
                "offset",
                "speaker",
                "utterance_idx",
            ],
        )
        # TODO: Decide what to do with the 'Multiple Speaker' tag
        # TODO: Checks for additional punctuation: '--'

    def agg_silences(self, silence_file):
        """Add silence information to transcript.

        Args:
            silence_file (DataFrame): Silence types, onsets, offsets.
        """
        # TODO: the audio cropping function should match this.

        # TODO: speaker and utterance_idx should be inherited where the silence type is not no speech.
        # Re-time transcript to adjust for cropped portions (silences)
        for onset, offset in zip(
            silence_file.silence_onsets, silence_file.silence_offsets
        ):
            self.transcript.loc[
                self.transcript.onset > self.origin + onset, ["onset", "offset"]
            ] += (offset - onset)

        # TODO: consider separating retiming and adding silences to transcript for flexibility.
        rep_val = len(silence_file.silences.silence_type)
        silence_df = pd.DataFrame(
            {
                "token_type": ["silence"] * rep_val,
                "token": silence_file.silences.silence_type,
                "onset": self.origin + silence_file.silence_onsets,
                "offset": self.origin + silence_file.silence_offsets,
                "speaker": [None] * rep_val,
                "utterance_idx": [None] * rep_val,
            }
        )

        self.transcript = (
            pd.concat([self.transcript, silence_df])
            .sort_values(by="onset")
            .reset_index(drop=True)
        )

    def add_dt(self, onset_day, onset_time):
        """Add audio date-time inofrmation.

        Args:
            onset_day (str)
            onset_time (str)
        """

        # TODO: Consider moving this for flexibility
        self.origin = pd.Timestamp(" ".join([onset_day, onset_time]))

        # To timestamps based on origin (onset date-time of audio file)
        self.transcript.onset += self.origin
        self.transcript.offset += self.origin

    def convert_timedelta(self):
        """Convert to timedelta."""
        self.transcript.onset = pd.to_timedelta(self.transcript.onset)
        self.transcript.offset = pd.to_timedelta(self.transcript.offset)

    def compress_transcript(self, factor):
        """Compress transcript.

        Args:
            factor (float): how much to compress times by.
        """
        # Adjust for 5% slow down
        self.transcript.onset = self.transcript.onset - self.transcript.onset * factor
        self.transcript.offset = (
            self.transcript.offset - self.transcript.offset * factor
        )
