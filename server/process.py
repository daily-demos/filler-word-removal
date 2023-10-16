import os
import uuid
from enum import Enum

from moviepy.video.compositing.concatenate import concatenate_videoclips
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip

from config import get_temp_dir_path, get_output_dir_path
from transcription.timestamp import Timestamps
from transcription import dg, whisper
from pathlib import Path


class Transcribers(Enum):
    Whisper = whisper
    Deepgram = dg


class Processor:
    transcriber = None
    id = None

    def __init__(
        self,
        transcriber=Transcribers.Deepgram,
    ):
        self.transcriber = transcriber.value
        self.id = uuid.UUID()


    def process(self, source_video_path: str):
        audio_file_path = self.extract_audio(source_video_path)
        result = self.transcribe(audio_file_path)
        split_times = self.get_splits(result)
        self.resplice(source_video_path, split_times)

    def extract_audio(self, video_path: str):
        video = VideoFileClip(video_path)
        audio_file_name = f'{Path(video_path).stem}.wav'
        audio_path = os.path.join(get_temp_dir_path(), audio_file_name)
        video.audio.write_audiofile(audio_path)
        return audio_path

    def transcribe(self, audio_path: str):
        return self.transcriber.transcribe(audio_path)

    def get_splits(self, result) -> Timestamps:
        return self.transcriber.get_splits(result)

    def resplice(self, source_video_path: str, splits: Timestamps):
        tmp = get_temp_dir_path()

        clips = []
        current_split = splits.head
        idx = 0
        try:
            while current_split:
                output_file_path = os.path.join(tmp, f"{str(idx)}.mp4")
                ffmpeg_extract_subclip(source_video_path, current_split.start, current_split.end, targetname=output_file_path)
                clips.append(VideoFileClip(output_file_path))
                current_split = current_split.next
                idx += 1
        except Exception as e:
            raise Exception("failed to split clips", e)

        try:
            final_clip = concatenate_videoclips(clips)
            output_file_name = f"{Path(source_video_path).stem}.mp4"
            output_file_path = os.path.join(get_output_dir_path(), output_file_name)
            final_clip.write_videofile(
                output_file_path,
                codec='libx264',
                audio_codec='aac',
                fps=60,
            )
        except Exception as e:
            raise Exception("failed to reconcatenate clips", e)

        for clip in clips:
            print("clip filenaem", clip.filename)
            os.remove(clip.filename)
