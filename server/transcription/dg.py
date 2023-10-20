"""This module implements Deepgram transcription and filler word removal split point detection
"""
import os

from deepgram import Deepgram
from . import timestamp

DEEPGRAM_TRANSCRIPTION_OPTIONS = {
    "model": "general",
    "tier": "nova",
    "filler_words": True,
    "language": "en",
}


def transcribe(audio_path: str):
    """Transcribes give audio file using Deepgram's Nova model"""
    deepgram_api_key = os.getenv("DEEPGRAM_API_KEY")
    if not deepgram_api_key:
        raise Exception("Deepgram API key is missing")
    if not os.path.exists(audio_path):
        raise Exception("Audio file could not be found", audio_path)
    try:
        deepgram = Deepgram(deepgram_api_key)
        with open(audio_path, 'rb') as audio_file:
            source = {'buffer': audio_file, 'mimetype': "audio/wav"}
            res = deepgram.transcription.sync_prerecorded(
                source, DEEPGRAM_TRANSCRIPTION_OPTIONS
            )
        return res
    except Exception as e:
        raise Exception("failed to transcribe with Deepgram") from e


def get_splits(result) -> timestamp.Timestamps:
    """Retrieves split points with detected filler words removed"""
    filler_triggers = ["um", "uh", "eh", "mmhm", "mm-mm"]
    words = get_words(result)
    splits = timestamp.Timestamps()
    first_split_start = 0
    try:
        for text in words:
            word = text["word"]
            word_start = text["start"]
            word_end = text["end"]
            if word in filler_triggers:
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
        splits.tail.end = words[-1]["end"]
        return splits
    except Exception as e:
        raise Exception("failed to split at filler words") from e


def get_words(result):
    """Retrieves list of words and their timestamps from Deepgram output"""
    res = result["results"]
    channels = res["channels"]
    channel = channels[0]
    alts = channel["alternatives"]
    alt = alts[0]
    words = alt["words"]
    return words
