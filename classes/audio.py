import taglib
import getpass
import numpy as np
from pydub import AudioSegment
from autologging import traced, logged


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

    def __init__(self, sid: str, file):
        """Initializes the instance based on file identifier.

        Args:
          fid: File identifier.
        """
        self.sid = sid
        self.in_name = file

        self.__log.info("User: " + getpass.getuser())

    def read_audio(self):
        """Read audio signal.

        Args:
          filepath: Path to audio file.
        """
        # TODO: option for reading multiple tracks?
        self.audio_track = AudioSegment.from_wav(self.in_name)
        # play(audioPart)
        # NOTE: pydub does things in milliseconds

    def crop_audio(self,silence_times):
        """Remove marked segments from audio. For uploading for transcription."""
        # TODO: The deid audio files might be split parts
        # TODO: Do more checks

        # Get speech times from silence times
        # extract sid and part
        # format
        speech_onsets = np.array(silence_times.silence_offsets.view(np.int64) / int(1e6))
        speech_offsets = np.roll(
            silence_times.silence_onsets.view(np.int64) / int(1e6), -1
        )

        # Remove consecutive non-speech labels
        speech_idxs = np.where((speech_offsets - speech_onsets) != 0)
        speech_times = zip(speech_onsets[speech_idxs], speech_offsets[speech_idxs])
        # Concat segments
        crop_audio = AudioSegment.empty()
        for time in speech_times:
            crop_audio += self.audio_track[time[0] : time[1]]
        self.transcribe_audio = crop_audio

    def slow_audio(self):
        """Slow down audio for transcription."""

        # slow_speed = 0.95
        # y_slow = librosa.effects.time_stretch(y, rate=slow_speed)
        sfaud = self.transcribe_audio._spawn(
            self.transcribe_audio.raw_data,
            overrides={"frame_rate": int(self.transcribe_audio.frame_rate * 0.95)},
        ).set_frame_rate(self.transcribe_audio.frame_rate)
        # sfaud = sound_with_altered_frame_rate.set_frame_rate(self.audioTrack.frame_rate)
        # breakpoint()
        self.transcribe_audio = sfaud

    def write_audio(self):
        """Write audio signal."""
        self.transcribe_audio.export(self.out_name, format="wav")
        with taglib.File(self.out_name, save_on_exit=True) as audio_file:
            audio_file.tags["startDateTime"] = "startDateTime"
            audio_file.tags["endDateTime"] = "endDateTime"
