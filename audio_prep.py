import logging
import glob
import os
import pandas as pd
import argparse
import whisperx
from classes.audio import Audio


def arg_parser():
    """Argument Parser

    Args:

    Returns:
        args (namespace): commandline arguments
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--sid", type=str, required=True)
    parser.add_argument("--conv-idx", type=str, required=True)
    parser.add_argument("--model", type=str, required=True)

    args = parser.parse_args()
    conv_list = sorted(glob.glob(f"data/tfs/{args.sid}/*"))
    conv_name = os.path.basename(conv_list[int(args.conv_idx) - 1])
    args.audio_filename = f"data/tfs/{args.sid}/{conv_name}/audio/{conv_name}_deid.wav"

    # for result_type in ["whisperx", "vad", "osd", "whisper"]:
    for result_type in ["whisper"]:
        if "whisper" in result_type:
            result_dir = os.path.join(
                "results", args.sid, f"{result_type}_{args.model}"
            )
        else:
            result_dir = os.path.join("results", args.sid, result_type)
        if not os.path.exists(result_dir):
            os.makedirs(result_dir)

    args.conv_name = conv_name
    args.out_filename = os.path.join("results", args.sid, f"%s/{conv_name}.csv")
    args.device = "cuda"

    return args


def main():

    args = arg_parser()

    audio = Audio(args.sid, args.conv_idx, args.audio_filename, args.device)

    # ### WHISPERX PIPELINE ###
    # datum = audio.whisperx_pipeline(args.model)
    # datum.to_csv(args.out_filename % f"whisperx_{args.model}", index=False)

    # ### PYANNOTE PIPELINE ###
    # vad_df = audio.pyannote_vad()
    # vad_df.to_csv(args.out_filename % "vad", index=False)
    # osd_df = audio.pyannote_osd()
    # osd_df.to_csv(args.out_filename % "osd", index=False)

    ### WHISPER PIPELINE ###
    audio.read_audio_whisper()
    datum = audio.whisper_transcribe(args.model)
    datum.to_csv(args.out_filename % f"whisper_{args.model}", index=False)

    return


if __name__ == "__main__":
    main()
