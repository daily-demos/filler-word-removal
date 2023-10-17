import json
import os
import sys
import traceback

from config import ensure_dirs, get_output_dir_path, get_upload_dir_path

from quart import Quart, request, jsonify, send_from_directory

app = Quart(__name__)

from quart_cors import cors
from project import Project

cors(app)
ensure_dirs()

processes = set()


@app.route('/upload', methods=['POST'])
async def upload_file():
    files = (await request.files)
    file = files["file"]
    file_name = file.filename
    file_path = os.path.join(get_upload_dir_path(), file_name)
    try:
        file.save(file_path)
    except Exception as e:
        traceback.print_exc()
        response = {'error': str(e)}
        return jsonify(response), 500
    project = Project()
    try:
        app.add_background_task(project.process, file_path)

        response = {'project_id': project.id, 'name': file_name}
        return jsonify(response), 200
    except Exception as e:
        traceback.print_exc()
        print("failed to start processing file:", e, file=sys.stderr)
        response = {'error': str(e)}
        return jsonify(response), 500


@app.route('/projects/<project_id>', methods=['GET'])
async def get_status(project_id):
    status_file_name = f'{project_id}.txt'
    status_file_path = os.path.join(get_output_dir_path(), status_file_name)
    try:
        with open(status_file_path, "r") as f:
            data = json.load(f)
            return jsonify(data), 200
    except Exception as e:
        msg = "failed to open status file"
        print(e, file=sys.stderr)
        return jsonify({'error': msg}), 500


@app.route('/projects/<project_id>/download', methods=['GET'])
async def download_final_output(project_id):
    output_file_name = f'{project_id}.mp4'
    return await send_from_directory(get_output_dir_path(), output_file_name, as_attachment=True)


if __name__ == '__main__':
    app.run(debug=True)
