from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import os
from flask import send_from_directory

from ocr_engine import run_ocr

app = Flask(__name__, static_url_path="/static")

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# expose the uploads path so I can upload images??
@app.route("/uploads/<path:filename>")
def uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

@app.route("/ocr", methods=["POST"])
def ocr_endpoint():
    # check file exists
    if "image" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["image"]
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(filepath)

    # 1. OCR
    text = run_ocr(filepath)

    # 4. Return everything to the frontend
    return jsonify({
        "text": text,
        "image_url": f"/uploads/{filename}"
    })


@app.route("/")
def index():
    return app.send_static_file("index.html")


if __name__ == "__main__":
    app.run(debug=True, port=8080)