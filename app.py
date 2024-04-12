import subprocess
from flask import Flask, request, jsonify, send_from_directory, render_template, redirect
import os


app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs('reports', exist_ok=True)


@app.route('/')
def index():
    files = os.listdir('reports')
    files_with_times = [(file, os.path.getmtime(os.path.join('reports', file))) for file in files]
    sorted_files = sorted(files_with_times, key=lambda x: x[1], reverse=True)
    recent_files = sorted_files[:5]
    recent_filenames = [file[0] for file in recent_files]
    return render_template('upload.html', files=recent_filenames)


@app.route('/upload', methods=['POST'])
def run_script():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file:
        # data = request.json
        # args = data.get('args', [])

        filename = file.filename
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)

        # command = ['python', 'TaaC-AI.py'] + args
        command = ['python', 'TaaC-AI.py', filepath]

        try:
            result = subprocess.run(command, capture_output=True, text=True, check=True)
            url = result.stdout.strip()
            if not url.startswith("reports"):
                return jsonify({"error": "Script execution failed", "details": result.stdout}), 400
            return redirect(url)
        except subprocess.CalledProcessError as e:
            return jsonify({"error": "Script execution failed", "details": e.stderr}), 400


@app.route("/reports/<path:filename>")
def serve_reports(filename):
    return send_from_directory('reports', filename)


if __name__ == "__main__":
    app.run(debug=True)
