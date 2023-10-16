from enum import Enum

import whisper_timestamped

from . import timestamp


class Models(Enum):
    TINY = "tiny"
    BASE = "base"
    MEDIUM = "medium"
    NBAILAB_LARGE_V2 = "NbAiLab/whisper-large-v2-nob"


def transcribe(audio_path: str):
    try:
        audio = whisper_timestamped.load_audio(audio_path)
        model = whisper_timestamped.load_model(Models.BASE.value, device="cpu")
        transcription = whisper_timestamped.transcribe(model, audio, detect_disfluencies=True, language="en", vad=False,
                                                       temperature=0, no_speech_threshold=1, min_word_duration=0)
    except Exception as e:
        raise Exception("failed to transcribe with Whisper", e)
    return transcription


def get_splits(transcription) -> timestamp.Timestamps:
    fillers = timestamp.Timestamps()
    segments = transcription["segments"]
    end_time = segments[-1]["end"]
    for segment in segments:
        for word in segment["words"]:
            text = word["text"]
            if "[*]" in text:
                fillers.add(word["start"], word["end"])

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
