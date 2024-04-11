import taglib
import getpass
import numpy as np
import pandas as pd
import os
import scipy.io.wavfile as wavfile
from pydub import AudioSegment
from autologging import traced, logged

from datetime import datetime

from pyannote.audio import Model, Pipeline
from pyannote.audio.pipelines import (
    VoiceActivityDetection,
    OverlappedSpeechDetection,
    SpeakerDiarization,
)
import torch
import torchaudio
import whisperx
import whisper
import gc


HF_TOKEN = os.environ["HF_TOKEN"]
WHISPER_FS = 16000


@traced
@logged
class Audio:
    """Information and data for each patient audio file.

    ...

    Attributes:
        sid: Unique subject indentifier, DType: str.
        name: Name of audio file, DType: str.
        base_path: Subject base directory, DType: PosixPath.
        audio_deid_path: Subject de-identified audio directory, DType: PosixPath.
        audio_transcribe_path: Subject transcription audio directory, DType: PosixPath.
        deid_audio: Data from de-identified audio file (input audio), DType: Pydub AudioSegment.
        transcribe_audio: Audio data for transcription (output audio), DType: Pydub AudioSegment.
    """

    def __init__(self, sid: str, conv_idx, file, device="cuda"):
        """Initializes the instance based on file identifier.

        Args:
          fid: File identifier.
        """
        self.sid = sid
        self.conv_idx = conv_idx
        self.audio_filename = file
        self.device = device

        self.reset_audio_info()

        self.__log.info("User: " + getpass.getuser())

    def reset_audio_info(self):
        self.audio_fs = None
        self.audio_len = None
        self.audio_sample_len = None

    def read_audio_print(self, package):
        """Read audio signal using pydub package.

        Args:
          package: package used to load audio
        """
        print(f"Loading {self.audio_filename} using {package} package")
        print(f"Sampling rate: {self.audio_fs}")
        print(f"Audio Length (s): {self.audio_len}")
        print(f"Total number of samples: {self.audio_sample_len}")

    def stereo_to_mono(self):
        """Convert stereo wav file to mono.

        Args:
          None
        """
        if self.audio.shape[0] > 1:
            print("Changing stereo to mono")
            self.audio = torch.mean(self.audio, dim=0, keepdim=True)

    def save_mono_pydub(self):
        """Convert stereo wav file to mono and overwrite original audiofile.

        Args:
          None
        """
        self.read_audio_pydub()
        self.audio.set_channels(1)
        self.audio.export(self.audio_filename, format="wav")

    def read_audio_pydub(self):
        """Read audio signal using pydub package.

        Args:
          filepath: Path to audio file.
        """
        self.reset_audio_info()
        self.audio = AudioSegment.from_wav(self.audio_filename)

    def read_audio_wavfile(self):
        """Read audio signal using wavfile package.

        Args:
          filepath: Path to audio file.
        """
        self.reset_audio_info()
        self.audio_fs, self.audio = wavfile.read(self.audio_filename)
        self.audio_sample_len = len(self.audio)
        self.audio_len = self.audio_sample_len / self.audio_fs
        self.read_audio_print("wavfile")

    def read_audio_torchaudio(self):
        """Read audio signal using torchaudio package.

        Args:
          filepath: Path to audio file.
        """
        self.reset_audio_info()
        # self.audio, self.audio_fs = torchaudio.load(
        #     self.audio_filename, normalize=False
        # )
        self.audio, self.audio_fs = torchaudio.load(self.audio_filename)
        self.audio_sample_len = self.audio.shape[1]
        self.audio_len = self.audio_sample_len / self.audio_fs
        self.read_audio_print("torchaudio")

    def read_audio_whisper(self):
        """Read audio signal using whisper package (downsamples to 16k).

        Args:
          filepath: Path to audio file.
        """
        self.reset_audio_info()
        self.audio = whisper.load_audio(self.audio_filename)
        self.audio_fs = WHISPER_FS
        self.audio_sample_len = len(self.audio)
        self.audio_len = self.audio_sample_len / self.audio_fs
        self.read_audio_print("whisper")

    def read_audio_whisperx(self):
        """Read audio signal using whisperx package (downsamples to 16k).

        Args:
          filepath: Path to audio file.
        """
        self.reset_audio_info()
        self.audio = whisperx.load_audio(self.audio_filename)
        self.audio_fs = WHISPER_FS
        self.audio_sample_len = len(self.audio)
        self.audio_len = self.audio_sample_len / self.audio_fs
        self.read_audio_print("whisperx")

    def whisperx_transcribe(self, model):
        """Transcribe using whisperx (VAD + transcription)

        Args:
          model: model-name
        """
        print("Transcribe with whisperx (batched)")
        batch_size = 16  # reduce if low on GPU mem
        compute_type = (
            "float16"  # change to "int8" if low on GPU mem (may reduce accuracy)
        )

        model = whisperx.load_model(model, self.device, compute_type=compute_type)
        self.transcribe_result = model.transcribe(
            self.audio, batch_size=batch_size, language="en"
        )

    def whisperx_align(self):
        """Align whisperx output using wav2vec 2.0 (Alignment)

        Args:
          None
        """
        print("Align whisper output")

        model_a, metadata = whisperx.load_align_model(
            language_code=self.transcribe_result["language"], device=self.device
        )
        self.transcribe_result = whisperx.align(
            self.transcribe_result["segments"],
            model_a,
            metadata,
            self.audio,
            self.device,
            return_char_alignments=False,
        )

    def whisperx_diarization(self):
        """Diarize whisperx output using pyannote (Diarization)

        Args:
          None
        """
        diarize_model = whisperx.DiarizationPipeline(
            use_auth_token=HF_TOKEN, device=self.device
        )
        diarize_segments = diarize_model(self.audio_filename)
        # diarize_model(args.audio_filename, min_speakers=2, max_speakers=3)
        self.transcribe_result = whisperx.assign_word_speakers(
            diarize_segments, self.transcribe_result
        )

    def whisperx_get_datum(self):
        """Format whisperx results into transcript datum

        Args:
          None
        """
        data = []
        word_idx = 0
        for segment in self.transcribe_result["segments"]:
            for word in segment["words"]:
                data.append(pd.DataFrame(word, index=[word_idx]))
                word_idx += 1
        datum = pd.concat(data)
        return datum

    def whisperx_pipeline(self, model):
        """Format whisperx results into transcript datum

        Args:
          None
        """
        self.read_audio_whisperx()
        self.whisperx_transcribe(model)
        self.whisperx_align()
        self.whisperx_diarization()
        return self.whisperx_get_datum()

    def pyannote_get_datum(self, input):
        """Retrn pyannote output as datum

        Args:
          input: pyannote output from vad or osd pipeline
        """
        df = pd.DataFrame(
            input.itertracks(yield_label=True), columns=["segment", "label", "speaker"]
        )
        df["start"] = df.segment.apply(lambda x: x.start)
        df["end"] = df.segment.apply(lambda x: x.end)
        df["sid"] = self.sid
        df["conv_idx"] = self.conv_idx
        df["audio_fs"] = self.audio_fs
        df["audio_sample_len"] = self.audio.shape[1]
        df = df.loc[
            :, ("sid", "conv_idx", "start", "end", "audio_fs", "audio_sample_len")
        ]
        return df

    def pyannote_vad(self):
        """Voice activity detection using pyannote

        Args:
          None
        """
        print("VAD with pyannote")
        HYPER_PARAMETERS = {
            # remove speech regions shorter than that many seconds.
            "min_duration_on": 0.0,
            # fill non-speech regions shorter than that many seconds.
            "min_duration_off": 10.0,
        }
        model = Model.from_pretrained(
            "pyannote/segmentation-3.0", use_auth_token=HF_TOKEN
        )
        pipeline = VoiceActivityDetection(segmentation=model)
        pipeline.instantiate(HYPER_PARAMETERS)
        vad = pipeline(self.audio_filename)
        vad_df = self.pyannote_get_datum(vad)
        return vad_df

    def pyannote_osd(self):
        """Overlapping speech detection using pyannote

        Args:
          None
        """
        print("OSD with pyannote")
        HYPER_PARAMETERS = {
            # remove speech regions shorter than that many seconds.
            "min_duration_on": 0.0,
            # fill non-speech regions shorter than that many seconds.
            "min_duration_off": 0.0,
        }
        model = Model.from_pretrained(
            "pyannote/segmentation-3.0", use_auth_token=HF_TOKEN
        )
        pipeline = OverlappedSpeechDetection(segmentation=model)
        pipeline.instantiate(HYPER_PARAMETERS)
        osd = pipeline(self.audio_filename)
        osd_df = self.pyannote_get_datum(osd)
        return osd_df

    def whisper_transcribe(self, model):
        """Transcribe using whisper (transcription)

        Args:
          model: model-name
        """
        model = whisper.load_model(model)
        transcribe_result = model.transcribe(self.audio, language="en")
        datum = pd.DataFrame(transcribe_result["segments"])
        datum = datum.loc[
            :,
            (
                "id",
                "seek",
                "start",
                "end",
                "text",
                "temperature",
                "avg_logprob",
                "compression_ratio",
                "no_speech_prob",
            ),
        ]
        return datum

    def crop_audio(self, silence_times):
        """Remove marked segments from audio. For uploading for transcription."""

    def write_audio(self):
        """Write audio signal."""
        self.transcribe_audio.export(self.out_name, format="wav")
        with taglib.File(self.out_name, save_on_exit=True) as audio_file:
            audio_file.tags["startDateTime"] = "startDateTime"
            audio_file.tags["endDateTime"] = "endDateTime"
