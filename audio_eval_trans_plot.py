import os
import glob
import argparse
import evaluate
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns


def plt_scatter(df, x, y, hue, name):
    fig, ax = plt.subplots()
    sns.scatterplot(data=df, x=x, y=y, hue=hue)
    # plt.scatter(df[x], df[y], s=10)
    ax.set_title(name)
    ax.set_xlabel(x)
    ax.set_ylabel(y)
    plt.savefig(f"results/{name}.jpeg")
    plt.close()
    return


def main():
    sids = [625, 676, 7170, 798]
    whisper_results = "results/%s/%s-whisper_inaudible.csv"
    whisper_results = "results/%s/%s-whisper.csv"

    total_df = pd.DataFrame()
    for sid in sids:
        sum_file = whisper_results % (sid, sid)
        sum_df = pd.read_csv(sum_file)
        sum_df["sid"] = str(sid)
        sum_df["prob"] = np.exp(sum_df.avg_logprob)
        total_df = pd.concat((total_df, sum_df))
        # for model in sum_df.model.unique():
        #     model_df = sum_df[sum_df.model == model]
        #     breakpoint()
        #     plt_scatter(model_df, "avg_logprob", "wer", f"{sid}_{model}_wer1")
        #     plt_scatter(model_df, "no_speech_prob", "wer", f"{sid}_{model}_wer2")
        #     plt_scatter(
        #         model_df, "no_speech_prob", "gt_word_num", f"{sid}_{model}_count"
        #     )
    # total_df = total_df[total_df.wer <= 1]
    # for model in total_df.model.unique():
    #     model_df = total_df[total_df.model == model]
    #     plt_scatter(model_df, "prob", "wer", "sid", f"{model}_wer1")
    #     plt_scatter(model_df, "no_speech_prob", "wer", "sid", f"{model}_wer2")
    #     plt_scatter(model_df, "no_speech_prob", "gt_word_num", "sid", f"{model}_count")
    #     plt_scatter(model_df, "no_speech_prob", "prob", "sid", f"{model}_count")

    total_df = total_df[total_df.sid != "798"]
    breakpoint()
    fig, ax = plt.subplots()
    sns.set_style("whitegrid")
    plt.yscale("log")
    plt.xscale("log")
    sns.histplot(data=total_df, x="wer", hue="model")
    plt.savefig(f"results/whisper-diff.jpeg")

    return


if __name__ == "__main__":
    main()
