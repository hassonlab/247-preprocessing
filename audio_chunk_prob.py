import os
import glob
import argparse
import pandas as pd
import numpy as np
import json

# import scipy.io.wavfile as wavfile
# from classes.audio import Audio
import diff_match_patch as dmp_module

DATUM_FILE_MAP = dict.fromkeys(["625", "676", "7170"], "*trimmed.txt")
DATUM_FILE_MAP["798"] = "*_datum_trimmed.txt"


# def chunk_first():
#     """
#     Sample chunks (7 per 0.1 prob, 70 per patient) and save wav, txt with 4 trans, and chunks csv
#     """

#     sids = [625, 676, 7170, 798]
#     whisper_results = "results/%s/%s-whisper_inaudible.csv"
#     whisper_results = "results/%s/%s-whisper.csv"

#     total_df = pd.DataFrame()
#     for sid in sids:
#         sum_file = whisper_results % (sid, sid)
#         sum_df = pd.read_csv(sum_file)
#         sum_df["sid"] = str(sid)
#         sum_df["prob"] = np.exp(sum_df.avg_logprob)
#         total_df = pd.concat((total_df, sum_df))

#     all_chunk_df = pd.DataFrame()
#     for sid in sids:
#         chunk_df = pd.DataFrame()
#         sid_df = total_df[total_df.sid == str(sid)]
#         sid_df = sid_df[sid_df.model == "whisper_large-v3"]

#         # sample 5 per 0.1 prob
#         for idx, prob_num in enumerate(np.arange(0, 1, 0.1)):
#             prob_df = sid_df[
#                 (sid_df.prob >= prob_num) & (sid_df.prob <= prob_num + 0.1)
#             ]
#             sample_num = min(7, len(prob_df))
#             prob_df = prob_df.sample(n=sample_num, replace=False)
#             prob_df.sort_values(by=["prob"], inplace=True)
#             chunk_df = pd.concat(
#                 (chunk_df, prob_df.loc[:, ("sid", "conversation", "chunk")])
#             )

#         # get transcriptions
#         grtr_csv = pd.read_csv(f"results/{sid}/{sid}-grtr-text.csv")
#         whisper_v2_csv = pd.read_csv(f"results/{sid}/{sid}-whisper_large-v2-text.csv")
#         whisper_v3_csv = pd.read_csv(f"results/{sid}/{sid}-whisper_large-v3-text.csv")
#         whisperx_v2_csv = pd.read_csv(f"results/{sid}/{sid}-whisperx_large-v2-text.csv")

#         chunk_df["chunk_name"] = np.arange(0, len(chunk_df)) + 1
#         chunk_df["chunk_str"] = f"{sid}_chunk"
#         chunk_df["chunk_name"] = chunk_df.chunk_str + chunk_df.chunk_name.astype(str)

#         for index, row in chunk_df.iterrows():
#             print(row["chunk_name"])
#             # read audio
#             audio_file = f"data/tfs/{sid}/{row['conversation']}/audio/{row['conversation']}_deid.wav"
#             audio = Audio(sid, 0, audio_file, "cuda")
#             audio.read_audio_wavfile()

#             # save audio chunk
#             chunk = row["chunk"]
#             chunk_start = chunk[1 : chunk.find(", ")]
#             chunk_end = chunk[chunk.find(", ") + 2 : -1]

#             chunk_data = audio.audio[
#                 int(float(chunk_start) * audio.audio_fs) : int(
#                     float(chunk_end) * audio.audio_fs
#                 )
#             ]
#             chunk_name = f"results_chunk/{row['chunk_name']}.wav"
#             wavfile.write(chunk_name, audio.audio_fs, chunk_data)

#             # save transcripts
#             trans_name = f"results_chunk/{row['chunk_name']}.txt"
#             try:
#                 grtr = grtr_csv.query(
#                     f'chunk == "{chunk}" and conversation == "{row["conversation"]}"'
#                 ).text.iloc[0]
#                 wv2 = whisper_v2_csv.query(
#                     f'chunk == "{chunk}" and conversation == "{row["conversation"]}"'
#                 ).text.iloc[0]
#                 wv3 = whisper_v3_csv.query(
#                     f'chunk == "{chunk}" and conversation == "{row["conversation"]}"'
#                 ).text.iloc[0]
#                 wx2 = whisperx_v2_csv.query(
#                     f'chunk == "{chunk}" and conversation == "{row["conversation"]}"'
#                 ).text.iloc[0]
#                 with open(trans_name, "a") as f:
#                     f.write("Groundtruth:\n")
#                     f.write(grtr)
#                     f.write("\nWhisper-large-v2:\n")
#                     f.write(wv2)
#                     f.write("\nWhisper-large-v3:\n")
#                     f.write(wv3)
#                     f.write("\nWhisperx-large-v2:\n")
#                     f.write(wx2)
#             except:
#                 print("Something went wrong")

#         all_chunk_df = pd.concat(
#             (
#                 all_chunk_df,
#                 chunk_df.loc[:, ("chunk_name", "sid", "conversation", "chunk")],
#             )
#         )
#     all_chunk_df.to_csv("results_chunk/all_chunks.csv", index=False)

#     return


def diff_linesToWords(text1, text2):
    """Split two texts into an array of strings.  Reduce the texts to a string
    of hashes where each Unicode character represents one line.

    Args:
      text1: First string.
      text2: Second string.

    Returns:
      Three element tuple, containing the encoded text1, the encoded text2 and
      the array of unique strings.  The zeroth element of the array of unique
      strings is intentionally blank.
    """
    lineArray = []  # e.g. lineArray[4] == "Hello\n"
    lineHash = {}  # e.g. lineHash["Hello\n"] == 4

    # "\x00" is a valid character, but various debuggers don't like it.
    # So we'll insert a junk entry to avoid generating a null character.
    lineArray.append("")

    def diff_linesToCharsMunge(text):
        """Split a text into an array of strings.  Reduce the texts to a string
        of hashes where each Unicode character represents one line.
        Modifies linearray and linehash through being a closure.

        Args:
          text: String to encode.

        Returns:
          Encoded string.
        """
        chars = []
        # Walk the text, pulling out a substring for each line.
        # text.split('\n') would would temporarily double our memory footprint.
        # Modifying text would create many large strings to garbage collect.
        lineStart = 0
        lineEnd = -1
        while lineEnd < len(text) - 1:
            lineEnd = text.find(" ", lineStart)
            if lineEnd == -1:
                lineEnd = len(text) - 1
            line = text[lineStart : lineEnd + 1]

            if line in lineHash:
                chars.append(chr(lineHash[line]))
            else:
                if len(lineArray) == maxLines:
                    # Bail out at 1114111 because chr(1114112) throws.
                    line = text[lineStart:]
                    lineEnd = len(text)
                lineArray.append(line)
                lineHash[line] = len(lineArray) - 1
                chars.append(chr(len(lineArray) - 1))
            lineStart = lineEnd + 1
        return "".join(chars)

    # Allocate 2/3rds of the space for text1, the rest for text2.
    maxLines = 666666
    chars1 = diff_linesToCharsMunge(text1)
    maxLines = 1114111
    chars2 = diff_linesToCharsMunge(text2)
    return (chars1, chars2, lineArray)


def diff_match(str1, str2):
    dmp = dmp_module.diff_match_patch()
    diff = dmp.diff_main(str1, str2)
    dmp.diff_cleanupSemantic(diff)
    return diff


def diff_match_word(str1, str2):
    dmp = dmp_module.diff_match_patch()
    lines = diff_linesToWords(str1, str2)
    diffs = dmp.diff_main(lines[0], lines[1], False)
    dmp.diff_charsToLines(diffs, lines[2])
    # dmp.diff_cleanupSemantic(diffs)
    return diffs


def diff_concat_str(diff):

    final_str = ""
    for chunk in diff:
        if chunk[0] == -1:
            final_str = final_str + "[" + chunk[1] + "]"
        elif chunk[0] == 0:
            final_str = final_str + chunk[1]
        elif chunk[0] == 1:
            final_str = final_str + "(" + chunk[1] + ")"
    return final_str


def diff_concat_df(diff, trans):

    final_str = []
    for chunk_idx, chunk in enumerate(diff):
        words = chunk[1].strip().split(" ")
        for word_idx, word in enumerate(words):
            word_str = word
            # if chunk[0] == -1 and word_idx == 0:
            #     word_str = "[" + word
            # elif chunk[0] == 1 and word_idx == 0:
            #     word_str = "(" + word
            # if chunk[0] == -1 and word_idx == len(words) - 1:
            #     word_str = word + "]"
            # elif chunk[0] == 1 and word_idx == len(words) - 1:
            #     word_str = word + ")"
            if chunk[0] != 1:
                if word == trans.word.iloc[0].lower():
                    final_str.append(
                        [
                            word_str,
                            chunk[0],
                            trans.start.iloc[0],
                            trans.end.iloc[0],
                            chunk_idx,
                        ]
                    )
                    trans = trans.iloc[1:, :]
                else:
                    final_str.append([word_str, chunk[0], np.nan, np.nan, chunk_idx])
            else:
                final_str.append([word_str, chunk[0], np.nan, np.nan, chunk_idx])
    final_str = pd.DataFrame(final_str)
    final_str.columns = ["word", "type", "onset", "offset", "chunk_idx"]
    final_str.bfill(inplace=True)
    final_str.ffill(inplace=True)
    return final_str


def get_transcript(datum_file):
    # original datum
    df = pd.read_csv(
        datum_file,
        sep=" ",
        header=None,
        names=["word", "onset", "offset", "accuracy", "speaker"],
    )
    df["word"] = df["word"].str.strip()
    df["start"] = (df.onset + 3000) / 512
    df["end"] = (df.offset + 3000) / 512
    # exclude_words = ["sp", "{lg}", "{ns}", "{LG}", "{NS}", "SP", "{inaudible}"]
    exclude_words = ["sp", "{lg}", "{ns}", "{LG}", "{NS}", "SP"]
    non_words = ["hm", "huh", "mhm", "mm", "oh", "uh", "uhuh", "um"]
    df = df[~df.word.isin(exclude_words)]
    df = df[~df.word.isin(non_words)]

    return df


def output_gecko_json(df):

    chunks = []
    for chunk_idx in df.chunk_idx.unique():
        chunk_df = df[df.chunk_idx == chunk_idx]
        terms = []
        for index, row in chunk_df.iterrows():
            term = {
                "start": round(row["onset"],2),
                "end": round(row["offset"],2),
                # "start": row["onset"],
                # "end": row["offset"],
                "text": row["word"],
                "type": "WORD",
            }
            terms.append(term)
        if chunk_df["type"].unique()[0] == 0:
            chunk_type = "[both]"
        elif chunk_df["type"].unique()[0] == 1:
            chunk_type = "[addition]"
        elif chunk_df["type"].unique()[0] == -1:
            chunk_type = "[deletion]"
        chunk = {
            "speaker": {"id": chunk_type, "name": ""},
            "start": round(chunk_df.onset.min(),2),
            "end": round(chunk_df.offset.max(),2),
            # "start": chunk_df.onset.min(),
            # "end": chunk_df.offset.max(),
            "terms": terms,
        }
        chunks.append(chunk)

    gecko_dict = {"schemaVersion": "2.0", "monologues": chunks}

    return gecko_dict


def chunk_second():
    """
    Take chunk csv, do diff match patch
    """

    chunk_df = pd.read_csv("results_chunk/all_chunks.csv")

    for index, row in chunk_df.iterrows():
        sid = str(row["sid"])
        grtr_csv = pd.read_csv(f"results/{sid}/{sid}-grtr-text.csv")
        # whisper_v2_csv = pd.read_csv(f"results/{sid}/{sid}-whisper_large-v2-text.csv")
        # whisper_v3_csv = pd.read_csv(f"results/{sid}/{sid}-whisper_large-v3-text.csv")
        whisperx_v2_csv = pd.read_csv(f"results/{sid}/{sid}-whisperx_large-v2-text.csv")

        grtr = grtr_csv.query(
            f'chunk == "{row.chunk}" and conversation == "{row.conversation}"'
        ).text.iloc[0]
        wx2 = whisperx_v2_csv.query(
            f'chunk == "{row.chunk}" and conversation == "{row.conversation}"'
        ).text.iloc[0]

        gt_file_path = glob.glob(
            f"data/tfs/{sid}/{row.conversation}/misc/{row.conversation}{DATUM_FILE_MAP[sid]}"
        )
        if len(gt_file_path) != 1:
            print("WRONG WRONG WRONG")
            breakpoint()
        transcript = get_transcript(gt_file_path[0])
        chunk_start = float(row.chunk[1 : row.chunk.find(", ")])
        chunk_end = float(row.chunk[row.chunk.find(", ") + 2 : -1])
        transcript = transcript[transcript.start >= chunk_start]
        transcript = transcript[transcript.end <= chunk_end]

        diff = diff_match_word(grtr.lower(), wx2.lower())
        final_str = diff_concat_df(diff, transcript)
        final_str2 = diff_concat_str(diff)

        final_str.onset = final_str.onset - chunk_start
        final_str.offset = final_str.offset - chunk_start
        gecko_dict = output_gecko_json(final_str)
        with open(f"results_chunk/{row.chunk_name}.json", "w") as f:
            json.dump(gecko_dict, f)
        breakpoint()

    return


def main():
    # chunk_first()
    chunk_second()

    return


if __name__ == "__main__":
    main()
