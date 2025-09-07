from flask import Flask, flash, request, redirect, url_for, render_template, jsonify, session
import pickle
import numpy as np
import pandas as pd
import os
import uuid
from werkzeug.utils import secure_filename

# ML models (optional imports)
from sklearn.ensemble import RandomForestClassifier, StackingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC

app = Flask(__name__)

# -------- Secret Key (important for session) --------
# You can replace with your own random string
app.secret_key = os.environ.get("SECRET_KEY", "supersecretkey123456")

# -------- Configuration --------
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'csv'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


# -------- Helpers --------
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def Predict(L):
    """Predict using saved ML model"""
    filename = 'finalized_model.sav'
    if not os.path.exists(filename):
        raise FileNotFoundError("Model file not found: finalized_model.sav")

    loaded_model = pickle.load(open(filename, 'rb'))
    P = loaded_model.predict_proba(np.array([L]))
    return P


# -------- Routes --------
@app.route("/")
def first():
    return render_template("index.html")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/precautions")
def precautions():
    return render_template("precautions.html")


@app.route("/home", methods=["GET", "POST"])
def home():
    return render_template("home.html")


@app.route("/Prediction", methods=["GET", "POST"])
def Samples():
    if request.method == "POST":
        data = request.json
        R = list(Predict(data)[0])
        return jsonify(R)
    return render_template("home.html")


@app.route("/model")
def model():
    return render_template("model.html")


@app.route("/form", methods=["GET", "POST"])
def form():
    return render_template("form.html")


@app.route("/login")
def login():
    return render_template("login.html")


# -------- File Upload --------
@app.route("/upload", methods=["GET", "POST"])
def upload():
    if request.method == 'POST':
        if 'datasetfile' not in request.files:
            flash('No file part', 'error')
            return redirect(request.url)

        file = request.files['datasetfile']

        if file.filename == '':
            flash('No file selected', 'error')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            try:
                filename = f"{uuid.uuid4().hex}_{secure_filename(file.filename)}"
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)

                # Store file path in session
                session['uploaded_file'] = filepath
                session['original_filename'] = file.filename

                flash('File successfully uploaded', 'success')
                return redirect(url_for('preview'))

            except Exception as e:
                flash(f'Error processing file: {str(e)}', 'error')
                return redirect(request.url)
        else:
            flash('Invalid file type. Only CSV files allowed.', 'error')
            return redirect(request.url)

    return render_template("upload.html")


# -------- Preview --------
@app.route("/preview", methods=["GET"])
def preview():
    if 'uploaded_file' not in session:
        flash('No file uploaded. Please upload a file first.', 'error')
        return redirect(url_for('upload'))

    try:
        filepath = session['uploaded_file']
        df = pd.read_csv(filepath)
        df_view = df.head(50)  # show first 50 rows

        return render_template("preview.html", df_view=df_view)

    except Exception as e:
        return f"Error loading preview: {str(e)}", 500


# -------- Dummy Train Route (AJAX from preview.html) --------
@app.route("/train_model", methods=["POST"])
def train_model():
    try:
        # Example training placeholder (replace with real ML pipeline)
        print("Training started...")
        # Simulate success
        return jsonify({"status": "success", "message": "Training complete!"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/chart")
def chart():
    return render_template("chart.html")


# -------- Run --------
if __name__ == "__main__":
    # Local run
    app.run(debug=True, host="0.0.0.0", port=5000)
