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
    parser.add_argument("--model", type=str, required=True)
    parser.add_argument("--conv-idx", type=str, required=True)

    args = parser.parse_args()
    conv_dir = f"data/tfs/{args.sid}/*"
    conv_list = sorted(glob.glob(conv_dir))
    conv_name = os.path.basename(conv_list[int(args.conv_idx)])
    args.audio_filename = f"data/tfs/{args.sid}/{conv_name}/audio/{conv_name}_deid.wav"

    result_dir = os.path.join("results", args.sid, f"{args.model}-x")
    if not os.path.exists(result_dir):
        os.makedirs(result_dir)

    args.out_filename = os.path.join(result_dir, f"{conv_name}.csv")
    args.device = "cuda"

    return args


def main():

    args = arg_parser()

    audio = Audio(args.sid, args.audio_filename, args.device)
    breakpoint()
    audio.read_audio_torchaudio()
    audio.read_audio_wavfile()

    return


if __name__ == "__main__":
    main()
