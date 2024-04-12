import numpy as np
import matplotlib.pyplot as plt
from scipy import signal


def edf_wav_shift(ecog_dict, audio):
    ecog = signal.decimate(np.array(ecog_dict[204]), 4)
    correlation = signal.correlate(
        np.abs(signal.hilbert(ecog)),
        np.abs(signal.hilbert(audio)),
        mode="full",
        method="fft",
    )
    n = len(ecog)
    # audio = audio[(len(audio)-len(ecog))+(512*60*5):-(512*60*5)]
    # correlation = signal.correlate(ecog, audio, mode='same') / np.sqrt(signal.correlate(ecog, audio, mode='same')[int(n/2)] * signal.correlate(ecog, audio, mode='same')[int(n/2)])
    delay_arr = np.linspace(-0.5 * n / 512, 0.5 * n / 512, n)
    lags = signal.correlation_lags(ecog.size, audio.size, mode="full")
    lag = lags[np.argmax(correlation)]
    plt.plot(delay_arr, correlation)
    plt.savefig("test.png")

    return
