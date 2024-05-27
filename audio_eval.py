import os
import glob
import argparse
import evaluate
import pandas as pd
import numpy as np


DATUM_FILE_MAP = dict.fromkeys(["625", "676", "7170"], "*trimmed.txt")
DATUM_FILE_MAP["798"] = "*_datum_trimmed.txt"


def evaluate_preds(transcript, transcript_pred):
    # evaluate
    metric = evaluate.load("wer")
    wer = metric.compute(predictions=transcript_pred, references=transcript)
    return wer


def evaluate_whisper_chunk(grtr, pred):
    pred_len = max(pred.start.max(), pred.end.max())
    bins = np.arange(0, pred_len, step=60)
    bins = np.append(bins, pred_len)
    grtr["chunk"] = pd.cut(grtr.start, bins)
    pred["chunk"] = pd.cut(pred.start, bins)
    grtr_grouped = grtr.groupby("chunk", observed=True)
    pred_grouped = pred.groupby("chunk", observed=True)

    results = []
    grtrs = []
    preds = []
    for (chunk1, grtr_group), (chunk2, pred_group) in zip(grtr_grouped, pred_grouped):
        result = []

        # grtr_group, pred_group = delete_inaudible(grtr_group, pred_group)
        # result.append(chunk1)
        # result.append(len(grtr_group))

        grtr_trans = " ".join(grtr_group.word.astype(str).tolist())
        pred_trans = " ".join(pred_group.word.astype(str).tolist())
        # result.append(len(pred_trans.split(" ")))
        grtrs.append([chunk1, grtr_trans])
        preds.append([chunk1, pred_trans])

        # if len(grtr_group) == 0 or len(pred_group) == 0:  # silence
        #     continue
        # wer = evaluate_preds([grtr_trans], [pred_trans])
        # # if wer >= 1.5:
        # #     breakpoint()
        # result.append(wer)
        # result.append(pred_group.temperature.mean())
        # result.append(pred_group.avg_logprob.mean())
        # result.append(pred_group.no_speech_prob.mean())

        # results.append(result)

    return results, grtrs, preds


def delete_inaudible(grtr_group, pred_group):
    inaud_tags = ["{inaudible}", "inaudible"]
    if sum(grtr_group.word.isin(inaud_tags)) > 0:
        inaud_grtr_group = grtr_group.sort_values(by="start")
        inaud_grtr_group["start"] = inaud_grtr_group.start.shift(-1)
        inaud_grtr_group["end"] = inaud_grtr_group.end.shift()
        inaud_grtr_group = inaud_grtr_group[inaud_grtr_group.word.isin(inaud_tags)]
        for idx in inaud_grtr_group.index:
            inaud_start = inaud_grtr_group.loc[idx, "end"]  # end of previous word
            inaud_end = inaud_grtr_group.loc[idx, "start"]  # start of next word
            # pred_group_len = len(pred_group)
            pred_group = pred_group[
                (pred_group.start <= inaud_start) | (pred_group.start >= inaud_end)
            ]
            # if len(pred_group) < pred_group_len:
            #     print(f"Deleted inaudible chunks: {pred_group_len - len(pred_group)}")
        grtr_group = grtr_group[~grtr_group.word.isin(inaud_tags)]
        return grtr_group, pred_group
    else:
        return grtr_group, pred_group

    return


def get_pred_whisper(predict_file):
    # get prediction
    df_pred = pd.read_csv(predict_file)
    df_pred["onset"] = df_pred.start * 512 - 3000
    df_pred["offset"] = df_pred.end * 512 - 3000
    df_pred["word"] = df_pred["text"].str.strip()
    df_pred["word"] = df_pred["word"].apply(  # getting rid of punctuations
        lambda x: str(x).translate(
            str.maketrans("", "", '!"#$%&()*+,-./:;<=>?@[\\]^_`{|}~')
        )
    )
    return df_pred


def get_pred_whisperx(predict_file):
    # get prediction
    df_pred = pd.read_csv(predict_file)
    df_pred["onset"] = df_pred.start * 512 - 3000
    df_pred["offset"] = df_pred.end * 512 - 3000
    df_pred["word"] = df_pred["word"].str.strip()
    df_pred["word"] = df_pred["word"].apply(  # getting rid of punctuations
        lambda x: str(x).translate(
            str.maketrans("", "", '!"#$%&()*+,-./:;<=>?@[\\]^_`{|}~')
        )
    )

    return df_pred


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


def get_speakers_utts(pred):
    pred["utt"] = pred.speaker.ne(pred.speaker.shift()).cumsum()

    def get_speaker_utts(groupdf):
        return len(groupdf.utt.unique())

    speakers_utts = pred.groupby(pred.speaker).apply(get_speaker_utts).tolist()
    return speakers_utts


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--sid", type=str, required=True)

    args = parser.parse_args()
    args.models = ["whisper_large-v2", "whisper_large-v3"]  # whisper
    args.models = ["whisperx_large-v2"]  # whisperx

    total_result = pd.DataFrame()
    for model_idx, model in enumerate(args.models):

        total_grtr = pd.DataFrame()
        total_pred = pd.DataFrame()

        print(f"Running {model}")
        conv_dir = f"results/{args.sid}/{model}/*"
        conv_files = sorted(glob.glob(conv_dir))
        for conv in conv_files:
            print(f"\tRunning {conv}")
            gt_file_string = os.path.basename(conv).replace(".csv", "")
            gt_file_path = glob.glob(
                f"data/tfs/{args.sid}/{gt_file_string}/misc/{gt_file_string}{DATUM_FILE_MAP[args.sid]}"
            )
            if len(gt_file_path) != 1:
                print("WRONG WRONG WRONG")
                breakpoint()
            transcript = get_transcript(gt_file_path[0])
            pred = get_pred_whisperx(conv)
            results, grtrs, preds = evaluate_whisper_chunk(transcript, pred)
            
            # results = pd.DataFrame(results)
            # results.columns = [
            #     "chunk",
            #     "gt_word_num",
            #     "pr_word_num",
            #     "wer",
            #     "temperature",
            #     "avg_logprob",
            #     "no_speech_prob",
            # ]
            # results["model"] = model
            # results["conversation"] = gt_file_string
            # total_result = pd.concat((total_result, results))

            grtrs = pd.DataFrame(grtrs)
            grtrs.columns = ["chunk", "text"]
            grtrs["conversation"] = gt_file_string
            total_grtr = pd.concat((total_grtr, grtrs))

            preds = pd.DataFrame(preds)
            preds.columns = ["chunk", "text"]
            preds["conversation"] = gt_file_string
            total_pred = pd.concat((total_pred, preds))

        total_pred.to_csv(
            f"results/{args.sid}/{args.sid}-{model}-text.csv", index=False
        )
        if model_idx == 0:
            total_grtr.to_csv(
                f"results/{args.sid}/{args.sid}-grtr-text.csv", index=False
            )

            # speakers_utts = get_speakers_utts(pred)
            # results["speakers_utts"] = np.tile(
            #     speakers_utts, (len(results), 1)
            # ).tolist()
    # total_result.to_csv(f"results/{args.sid}/{args.sid}-whisperx.csv", index=False)

    return


if __name__ == "__main__":
    main()
