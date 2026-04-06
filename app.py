import threading
from pathlib import Path
from typing import Dict, List

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

from backend.config import INPUT_DIR, OUTPUT_DIR
from backend.pipeline import run_full_pipeline
from backend.utils import ensure_empty_dir, new_job_id

app = Flask(__name__, static_folder="frontend", static_url_path="")
CORS(app)

JOBS: Dict[str, Dict] = {}


def _process_job(job_id: str, uploaded_paths: List[Path]):
    workspace = OUTPUT_DIR / job_id
    ensure_empty_dir(workspace)

    def set_status(message: str):
        JOBS[job_id]["status"] = message

    try:
        outputs = run_full_pipeline(uploaded_paths, workspace, set_status)
        JOBS[job_id]["done"] = True
        JOBS[job_id]["outputs"] = {
            key: value.replace(str(OUTPUT_DIR), "/outputs") for key, value in outputs.items()
        }
        JOBS[job_id]["status"] = "Completed"
    except Exception as exc:  # broad for demo reliability
        JOBS[job_id]["done"] = True
        JOBS[job_id]["error"] = str(exc)
        JOBS[job_id]["status"] = "Failed"


@app.route("/")
def index():
    return app.send_static_file("index.html")


@app.route("/api/reconstruct", methods=["POST"])
def reconstruct():
    files = request.files.getlist("images")
    if len(files) < 3:
        return jsonify({"error": "Upload at least 3 images."}), 400

    job_id = new_job_id()
    input_dir = INPUT_DIR / job_id
    ensure_empty_dir(input_dir)

    uploaded_paths = []
    for i, f in enumerate(files):
        ext = Path(f.filename or "img.jpg").suffix or ".jpg"
        out = input_dir / f"upload_{i:03d}{ext.lower()}"
        f.save(str(out))
        uploaded_paths.append(out)

    JOBS[job_id] = {
        "done": False,
        "status": "Queued",
        "outputs": {},
    }

    thread = threading.Thread(target=_process_job, args=(job_id, uploaded_paths), daemon=True)
    thread.start()

    return jsonify({"job_id": job_id})


@app.route("/api/status/<job_id>")
def status(job_id: str):
    if job_id not in JOBS:
        return jsonify({"error": "Job not found"}), 404
    return jsonify(JOBS[job_id])


@app.route("/outputs/<path:filepath>")
def output_files(filepath: str):
    return send_from_directory(OUTPUT_DIR, filepath)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
