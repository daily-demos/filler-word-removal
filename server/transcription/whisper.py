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
    first_split_start = 0
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
                    else:
                        # If this is the very first word, be sure to start
                        # the first split _after_ this one ends.
                        first_split_start = word_end

                # If this is not a filler word and there are no other words
                # already registered, add the first split.
                elif splits.count == 0:
                    splits.add(first_split_start, -1)
        splits.tail.end = segments[-1]["end"]
        return splits
    except Exception as e:
        raise Exception("failed to split at filler words") from e
