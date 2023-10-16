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
    deepgram_api_key = os.getenv("DEEPGRAM_API_KEY")
    if not deepgram_api_key:
        raise Exception("Deepgram API key is missing")

    try:
        deepgram = Deepgram(deepgram_api_key)
        if not os.path.exists(audio_path):
            raise Exception("Audio file could not be found", audio_path)
        with open(audio_path, 'rb') as audio_file:
            source = {'buffer': audio_file, 'mimetype': "audio/wav"}
            res = deepgram.transcription.sync_prerecorded(
                source, DEEPGRAM_TRANSCRIPTION_OPTIONS
            )
        return res
    except Exception as e:
        raise Exception("failed to transcribe with Deepgram", e)


def get_splits(result) -> timestamp.Timestamps:
    filler_triggers = ["um", "uh", "mmhm", "mm-mm"]
    fillers = timestamp.Timestamps()

    res = result["results"]
    channels = res["channels"]
    channel = channels[0]
    alts = channel["alternatives"]
    alt = alts[0]
    words = alt["words"]
    end_time = words[-1]["end"]

    try:
        for text in words:
            word = text["word"]
            for filler in filler_triggers:
                if filler in word:
                    fillers.add(text["start"], text["end"])
    except Exception as e:
        raise Exception("failed to compile filler words", e)

    splits = timestamp.Timestamps()
    current_filler = fillers.head
    while current_filler:
        start = 0
        end = current_filler.start
        if current_filler.prev is not None:
            start = current_filler.prev.end

        # Safeguard against empty or nonsensical splits
        if end > 0 and start != end:
            splits.add(start, end)

        current_filler = current_filler.next

    splits.add(fillers.tail.end, end_time)
    return splits
