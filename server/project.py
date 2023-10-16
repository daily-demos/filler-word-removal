import json
import os
import sys
import traceback
import uuid
from enum import Enum

from moviepy.video.compositing.concatenate import concatenate_videoclips
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip

from config import get_project_temp_dir_path, get_project_output_file_path, get_project_status_file_path
from transcription.timestamp import Timestamps
from transcription import dg, whisper
from pathlib import Path


class Transcribers(Enum):
    Whisper = whisper
    Deepgram = dg


class Status(Enum):
    InProgress = "In progress"
    Failed = "Failed"
    Done = "Succeeded"


class Project:
    transcriber = None
    id = None

    def __init__(
            self,
            transcriber=Transcribers.Whisper,
    ):
        self.transcriber = transcriber.value
        self.id = self.configure()

    def configure(self):
        id = uuid.uuid4()
        temp_dir = get_project_temp_dir_path(id)
        if os.path.exists(temp_dir):
            # Directory already exists, which indicates a conflict.
            # Pick a new UUID and try again
            return self.configure()
        os.makedirs(temp_dir)
        return id

    def process(self, source_video_path: str):
        print("LIZA PROCESSS STARTRD")
        self.update_status(Status.InProgress, '')
        try:
            audio_file_path = self.extract_audio(source_video_path)
        except Exception as e:
            traceback.print_exc()
            print(e, file=sys.stderr)
            self.update_status(Status.Failed, 'failed to extract audio file')
            return


        try:
            result = self.transcribe(audio_file_path)
        except Exception as e:
            traceback.print_exc()
            print(e, file=sys.stderr)
            self.update_status(Status.Failed, 'failed to transcribe audio')
            return

        try:
            split_times = self.get_splits(result)
        except Exception as e:
            traceback.print_exc()
            print(e, file=sys.stderr)
            self.update_status(Status.Failed, 'failed to get split segments')
            return

        try:
            self.resplice(source_video_path, split_times)
        except Exception as e:
            traceback.print_exc()
            print(e, file=sys.stderr)
            self.update_status(Status.Failed, 'failed to resplice video')
            return

        self.update_status(Status.Done, 'output file ready for download')

    def extract_audio(self, video_path: str):
        video = VideoFileClip(video_path)
        audio_file_name = f'{Path(video_path).stem}.wav'
        audio_path = os.path.join(get_project_temp_dir_path(self.id), audio_file_name)
        try:
            video.audio.write_audiofile(audio_path)
        except Exception as e:
            raise Exception("failed to save extracted audio file", e)
        return audio_path

    def transcribe(self, audio_path: str):
        return self.transcriber.transcribe(audio_path)

    def get_splits(self, result) -> Timestamps:
        return self.transcriber.get_splits(result)

    def resplice(self, source_video_path: str, splits: Timestamps):
        tmp = get_project_temp_dir_path(self.id)

        clips = []
        current_split = splits.head
        idx = 0
        try:
            while current_split:
                clip_file_path = os.path.join(tmp, f"{str(idx)}.mp4")
                ffmpeg_extract_subclip(source_video_path, current_split.start, current_split.end,
                                       targetname=clip_file_path)
                clips.append(VideoFileClip(clip_file_path))
                current_split = current_split.next
                idx += 1
        except Exception as e:
            raise Exception("failed to split clips", e)

        try:
            final_clip = concatenate_videoclips(clips)

            output_file_path = get_project_output_file_path(self.id)
            final_clip.write_videofile(
                output_file_path,
                codec='libx264',
                audio_codec='aac',
                fps=60,
            )
        except Exception as e:
            raise Exception("failed to reconcatenate clips", e)

        for clip in clips:
            os.remove(clip.filename)

    def update_status(self, status: Status, info: str):
        print("updating status", status, info)
        status = {
            'status': status.value,
            'info': info,
        }
        if status is Status.Done:
            status['download_url'] = get_project_output_file_path(self.id)

        status_file_path = get_project_status_file_path(self.id)
        with open(status_file_path, "w+") as f:
            f.write(json.dumps(status))
