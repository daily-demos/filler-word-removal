import os
import sys

from config import ensure_dirs, get_output_dir_path, get_upload_dir_path
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from process import Processor

app = Flask(__name__)
CORS(app)
ensure_dirs()

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        file = request.files['file']
        file_path = os.path.join(get_upload_dir_path(), file.filename)
        file.save(file_path)

        processor = Processor()
        try:
            processor.process(file_path)
        except Exception as e:
            print(e, file=sys.stderr)

        download_url = f'http://127.0.0.1:5000/processed/{file.filename}'
        response = {'download_url': download_url}
        return jsonify(response), 200
    except Exception as e:
        response = {'error': str(e)}
        return jsonify(response), 500


@app.route('/projects/<file>', methods=['GET'])
def download_final_output(file):
    return send_from_directory(get_output_dir_path(), file, as_attachment=True)


if __name__ == '__main__':
    app.run(debug=True)
