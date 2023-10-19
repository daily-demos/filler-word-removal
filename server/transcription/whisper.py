"""This module implements Whisper transcription with a locally-downloaded model."""

from enum import Enum

import whisper_timestamped

from . import timestamp


class Models(Enum):
    """Class of basic Whisper model selection options"""
    TINY = "tiny"
    BASE = "base"
    MEDIUM = "medium"
    NBAILAB_LARGE_V2 = "NbAiLab/whisper-large-v2-nob"


def transcribe(audio_path: str):
    """Transcribes given audio file using Whisper"""
    try:
        audio = whisper_timestamped.load_audio(audio_path)
        model = whisper_timestamped.load_model(Models.BASE.value, device="cpu")
        transcription = whisper_timestamped.transcribe(
            model,
            audio,
            detect_disfluencies=True,
            language="en",
            vad=False,
            temperature=0,
            no_speech_threshold=1,
            min_word_duration=0
        )
    except Exception as e:
        raise Exception("failed to transcribe with Whisper") from e
    return transcription


def get_splits(transcription) -> timestamp.Timestamps:
    """Retrieves split points with detected filler words removed"""
    segments = transcription["segments"]
    splits = timestamp.Timestamps()
    try:
        for segment in segments:
            for word in segment["words"]:
                text = word["text"]
                word_start = word["start"]
                word_end = word["end"]
                if "[*]" in text:
                    # If non-filler tail already exists, set the end time to the start of this filler word
                    if splits.tail:
                        splits.tail.end = word_start

                    # If previous non-filler's start time is not the same as the start time of this filler,
                    # add a new split.
                    if splits.tail.start != word_start:
                        splits.add(word_end, -1)
                # If this is not a filler word and there are no other words
                # already registered, add the first split.
                elif splits.count == 0:
                    splits.add(word_start, -1)
        splits.tail.end = segments[-1]["end"]
        return splits
    except Exception as e:
        raise Exception("failed to compile filler words") from e
