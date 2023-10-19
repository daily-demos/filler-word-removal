"""This module defines all the routes for the filler-word removal server."""
import json
import os
import sys
import traceback

from daily import fetch_recordings, get_access_link
from project import Project, Transcribers
from quart_cors import cors

import quart
import requests

from config import ensure_dirs, get_output_dir_path, get_upload_dir_path

from quart import Quart, request, jsonify, send_from_directory

app = Quart(__name__)
cors(app)
ensure_dirs()


@app.route('/upload', methods=['POST'])
async def upload_file():
    """Saves uploaded MP4 file and starts processing.
    Returns project ID"""
    files = await request.files
    file = files["file"]
    project = Project()
    file_name = f'{project.id}.mp4'
    file_path = os.path.join(get_upload_dir_path(), file_name)
    try:
        await file.save(file_path)
        if not os.path.exists(file_path):
            raise Exception("uploaded file not saved", file_path)
    except Exception as e:
        return process_error('failed to save uploaded file', e)

    return process(project, file_path, file_name)


@app.route('/process_recording/<recording_id>', methods=['POST'])
async def process_recording(recording_id):
    """Processes a Daily recording by given recording ID."""
    access_link = get_access_link(recording_id)

    # Download recording to UPLOAD dir
    try:
        data = requests.get(access_link, timeout=10)
    except Exception as e:
        return process_error('failed to download Daily recording', e)

    project = Project()
    file_name = f'{project.id}.mp4'
    file_path = os.path.join(get_upload_dir_path(), file_name)
    try:
        with open(file_path, 'wb') as file:
            file.write(data.content)
    except Exception as e:
        return process_error('failed to save Daily recording file', e)

    return process(project, file_path, file_name)


def process(project: Project, file_path: str, file_name: str) -> tuple[quart.Response, int]:
    """Runs filler-word-removal processing on given file."""
    try:
        app.add_background_task(project.process, file_path)

        response = {'project_id': project.id, 'name': file_name}
        return jsonify(response), 200
    except Exception as e:
        return process_error('failed to start processing file', e)


@app.route('/projects/<project_id>', methods=['GET'])
async def get_status(project_id):
    """Route to return current processing status of a project."""
    status_file_name = f'{project_id}.txt'
    status_file_path = os.path.join(get_output_dir_path(), status_file_name)
    try:
        with open(status_file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return jsonify(data), 200
    except Exception as e:
        msg = "failed to open status file"
        print(e, file=sys.stderr)
        return jsonify({'error': msg}), 500


@app.route('/projects/<project_id>/download', methods=['GET'])
async def download_final_output(project_id):
    """Route to download final processed output file."""
    output_file_name = f'{project_id}.mp4'
    return await send_from_directory(get_output_dir_path(), output_file_name, as_attachment=True)


@app.route('/recordings', methods=['GET'])
async def get_daily_recordings():
    """Route to fetch all Daily recordings from configured domain."""
    try:
        recordings = fetch_recordings()
        return jsonify({'recordings': recordings}), 200

    except Exception as e:
        msg = "failed to fetch Daily recordings. Is the Daily API key configured?"
        print(msg, e, file=sys.stderr)
        return jsonify({'error': msg}), 500


def process_error(msg: str, error: Exception) -> tuple[quart.Response, int]:
    """Prints provided error and returns appropriately-formatted response."""
    traceback.print_exc()
    print(msg, error, file=sys.stderr)
    response = {'error': msg}
    return jsonify(response), 500


if __name__ == '__main__':
    app.run(debug=True)
