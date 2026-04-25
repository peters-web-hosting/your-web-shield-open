import logging
import pathlib

from flask import Flask, redirect, render_template_string, request, send_file, url_for
from werkzeug.utils import secure_filename

from logdata import LogData


FILES_DIR = pathlib.Path("files")
OUTPUT_DIR = pathlib.Path("data")
ALLOWED_EXTENSIONS = {".txt", ".log"}

app = Flask(__name__)


def _allowed_file(filename: str) -> bool:
    return pathlib.Path(filename).suffix.lower() in ALLOWED_EXTENSIONS


def _output_files():
    if not OUTPUT_DIR.exists():
        return []
    return sorted([p for p in OUTPUT_DIR.iterdir() if p.is_file()])


@app.route("/", methods=["GET"])
def index():
    message = request.args.get("message", "")
    error = request.args.get("error", "")
    return render_template_string(
        """
        <!doctype html>
        <html>
          <head>
            <title>Your Web Shield</title>
            <style>
              body { font-family: Arial, sans-serif; margin: 2rem; max-width: 720px; }
              .box { border: 1px solid #ddd; border-radius: 8px; padding: 1rem; margin-bottom: 1rem; }
              .error { color: #b00020; }
              .success { color: #0a7f2e; }
            </style>
          </head>
          <body>
            <h1>🛡️ Your Web Shield</h1>
            <p>Upload a web server log file and run analysis.</p>

            <div class="box">
              <form action="/analyze" method="post" enctype="multipart/form-data">
                <input type="file" name="log_file" accept=".txt,.log" required />
                <button type="submit">Analyze uploaded file</button>
              </form>
              {% if error %}<p class="error">{{ error }}</p>{% endif %}
              {% if message %}<p class="success">{{ message }}</p>{% endif %}
            </div>

            {% if outputs %}
              <div class="box">
                <h2>Generated output files</h2>
                <ul>
                {% for output in outputs %}
                  <li><a href="{{ url_for('download_file', filename=output.name) }}">{{ output.name }}</a></li>
                {% endfor %}
                </ul>
              </div>
            {% endif %}
          </body>
        </html>
        """,
        message=message,
        error=error,
        outputs=_output_files(),
    )


@app.route("/analyze", methods=["POST"])
def analyze():
    uploaded_file = request.files.get("log_file")
    if uploaded_file is None or uploaded_file.filename == "":
        return redirect(url_for("index", error="Please select a file to upload."))

    safe_name = secure_filename(uploaded_file.filename)
    if not _allowed_file(safe_name):
        return redirect(url_for("index", error="Only .txt and .log files are supported."))

    FILES_DIR.mkdir(parents=True, exist_ok=True)
    destination = FILES_DIR / safe_name
    uploaded_file.save(destination)

    try:
        LogData(destination.name)
    except Exception:
        logging.exception("Failed to analyze uploaded file: %s", safe_name)
        return redirect(url_for("index", error="Analysis failed. Please check your log format and try again."))

    return redirect(url_for("index", message=f"Analysis complete for {safe_name}."))


@app.route("/download/<path:filename>", methods=["GET"])
def download_file(filename: str):
    safe_name = secure_filename(filename)
    path = OUTPUT_DIR / safe_name
    if not path.exists() or not path.is_file():
        return redirect(url_for("index", error="Requested file does not exist."))
    return send_file(path, as_attachment=True, download_name=safe_name)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8501, debug=False)
