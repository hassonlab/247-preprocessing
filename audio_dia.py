import logging
import glob
import os
import numpy as np
import pandas as pd
import argparse
import whisperx
from classes.audio import Audio

import torch
import torchaudio
from pyannote.audio import Model, Pipeline

HF_TOKEN = os.environ["HF_TOKEN"]
SAMPLE_RATE = 44100


def pyannote_diarization(args, audio, sample_rate):
    """Diarization and speaker embeddings with pyannote
    Args:
      None
    """
    print("Diarization with Pyannote")
    # Diarization
    pipeline3 = Pipeline.from_pretrained(
        "pyannote/speaker-diarization-3.1", use_auth_token=HF_TOKEN
    )
    pipeline3.to(torch.device("cuda"))
    dia, speaker_embs = pipeline3(
        {"waveform": audio, "sample_rate": sample_rate}, return_embeddings=True
    )

    # Get diarization dataframe
    dia_df = pd.DataFrame(
        dia.itertracks(yield_label=True), columns=["segment", "label", "speaker"]
    )
    dia_df["start"] = dia_df.segment.apply(lambda x: x.start)
    dia_df["end"] = dia_df.segment.apply(lambda x: x.end)
    dia_df["len"] = audio.shape[1] / sample_rate
    dia_df["sid"] = args.sid
    dia_df = dia_df.loc[:, ("sid", "speaker", "start", "end", "len")]

    # Get speaker embedding dataframe
    speaker_df = pd.DataFrame()
    speaker_df["speaker"] = dia.labels()
    speaker_df["embs"] = speaker_embs.tolist()
    speaker_df["sid"] = args.sid

    return dia_df, speaker_df


def arg_parser():
    """Argument Parser

    Args:

    Returns:
        args (namespace): commandline arguments
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--sid", type=str, required=True)
    parser.add_argument("--conv-idx", nargs="+", type=int, default=-1)

    args = parser.parse_args()
    conv_dir = f"data/tfs/{args.sid}/*"
    conv_list = [os.path.basename(conv) for conv in sorted(glob.glob(conv_dir))]
    if args.conv_idx == -1:
        args.conv_list = conv_list
    else:
        args.conv_list = [conv_list[i - 1] for i in args.conv_idx]
    args.audio_filename = f"data/tfs/{args.sid}/%s/audio/%s_deid.wav"
    args.vad_filename = f"results/{args.sid}/vad/%s.csv"
    args.out_filename = f"results/{args.sid}/%s.csv"

    args.device = "cuda"

    return args


def main():

    args = arg_parser()

    all_vad_df = pd.DataFrame()
    all_audio = []
    for idx, conv in enumerate(args.conv_list):
        print(idx, conv)
        audio = Audio(args.sid, idx, args.audio_filename % (conv, conv), args.device)
        audio.read_audio_torchaudio()
        audio.stereo_to_mono()
        assert audio.audio_fs == SAMPLE_RATE
        vad_df = pd.read_csv(args.vad_filename % conv)
        vad_df["sample_start"] = (vad_df.start * audio.audio_fs).astype(int)
        vad_df["sample_end"] = (vad_df.end * audio.audio_fs).astype(int)
        vad_df["conv"] = conv

        def get_audio_segment(start, end):
            return audio.audio[:, int(start) : int(end)]

        audio_segments = vad_df.apply(
            lambda x: get_audio_segment(x.sample_start, x.sample_end), axis=1
        )
        conv_audio = torch.cat(audio_segments.tolist(), dim=1)
        all_vad_df = pd.concat((all_vad_df, vad_df))
        all_audio.append(conv_audio)

    all_audio = torch.cat(all_audio, dim=1)
    print(f"Total size: {all_audio.shape[1]}")

    dia_df, speaker_df = pyannote_diarization(args, all_audio, SAMPLE_RATE)

    all_vad_df.to_csv(args.out_filename % "vad_chunks", index=False)
    dia_df.to_csv(args.out_filename % "dia", index=False)
    speaker_df.to_csv(args.out_filename % "speaker", index=False)

    return


if __name__ == "__main__":
    main()
