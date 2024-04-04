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

    def __init__(self, sid: str, file, device="cuda"):
        """Initializes the instance based on file identifier.

        Args:
          fid: File identifier.
        """
        self.sid = sid
        self.audio_filename = file
        self.device = device

        self.__log.info("User: " + getpass.getuser())

    def read_audio_pydub(self):
        """Read audio signal using pydub package.

        Args:
          filepath: Path to audio file.
        """
        print(f"Loading {self.audio_filename} using pydub package")
        self.audio = AudioSegment.from_wav(self.audio_filename)

    def read_audio_wavfile(self):
        """Read audio signal using wavfile package.

        Args:
          filepath: Path to audio file.
        """
        self.audio_fs, self.audio = wavfile.read(self.audio_filename)
        print(f"Loading {self.audio_filename} using wavfile package")
        print(f"Sampling rate: {self.audio_fs}")
        print(f"Audio Length (s): {len(self.audio) / self.audio_fs}")

    def read_audio_torchaudio(self):
        """Read audio signal using torchaudio package.

        Args:
          filepath: Path to audio file.
        """
        self.audio, self.audio_fs = torchaudio.load(self.audio_filename, normalize=False)
        print(f"Loading {self.audio_filename} using torchaudio package")
        print(f"Sampling rate: {self.audio_fs}")

    def read_audio_whisper(self):
        """Read audio signal using whisper package (downsamples to 16k).

        Args:
          filepath: Path to audio file.
        """
        print(f"Loading {self.audio_filename} using whisperx package")
        self.audio = whisper.load_audio(self.audio_filename)

    def read_audio_whisperx(self):
        """Read audio signal using whisperx package (downsamples to 16k).

        Args:
          filepath: Path to audio file.
        """
        print(f"Loading {self.audio_filename} using whisperx package")
        self.audio = whisperx.load_audio(self.audio_filename)

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
        for segment in self.result["segments"]:
            for word in segment["words"]:
                data.append(pd.DataFrame(word, index=[word_idx]))
                word_idx += 1
        self.datum = pd.concat(data)

    def whisperx_pipeline(self, model):
        """Format whisperx results into transcript datum

        Args:
          None
        """
        self.whisperx_transcribe(model)
        self.whisperx_align()
        self.whisperx_diarization()
        self.whisperx_get_datum()

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
        self.vad_df = pd.DataFrame(
            vad.itertracks(yield_label=True), columns=["segment", "label", "speaker"]
        )
        self.vad_df["start"] = self.vad_df.segment.apply(lambda x: x.start)
        self.vad_df["end"] = self.vad_df.segment.apply(lambda x: x.end)

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
        self.osd_df = pd.DataFrame(
            osd.itertracks(yield_label=True), columns=["segment", "label", "speaker"]
        )
        self.osd_df["start"] = self.osd_df.segment.apply(lambda x: x.start)
        self.osd_df["end"] = self.osd_df.segment.apply(lambda x: x.end)

    def pyannote_diarization(self):
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
        waveform, sample_rate = torchaudio.load(self.audio_filename)
        dia, speaker_embs = pipeline3(
            {"waveform": waveform, "sample_rate": sample_rate}, return_embeddings=True
        )
        self.dia_df = pd.DataFrame(
            dia.itertracks(yield_label=True), columns=["segment", "label", "speaker"]
        )
        self.dia_df["start"] = self.dia_df.segment.apply(lambda x: x.start)
        self.dia_df["end"] = self.dia_df.segment.apply(lambda x: x.end)
        self.dia_df["len"] = waveform.shape[1] / sample_rate
        self.dia_df["sid"] = self.sid
        self.dia_df["conv"] = self.conv_idx
        self.dia_df = self.dia_df.loc[
            :, ("sid", "conv", "speaker", "start", "end", "len")
        ]

        self.speaker_df = pd.DataFrame()
        self.speaker_df["speaker"] = dia.labels()
        self.speaker_df["embs"] = speaker_embs.tolist()
        self.speaker_df["conv"] = self.conv_idx
        self.speaker_df["sid"] = self.sid

    def whisper_transcribe(self, model):
        """Transcribe using whisper (transcription)

        Args:
          model: model-name
        """
        model = whisper.load_model("tiny.en")
        self.transcribe_result = model.transcribe(self.audio, language="en")

    def crop_audio(self, silence_times):
        """Remove marked segments from audio. For uploading for transcription."""

    def write_audio(self):
        """Write audio signal."""
        self.transcribe_audio.export(self.out_name, format="wav")
        with taglib.File(self.out_name, save_on_exit=True) as audio_file:
            audio_file.tags["startDateTime"] = "startDateTime"
            audio_file.tags["endDateTime"] = "endDateTime"
