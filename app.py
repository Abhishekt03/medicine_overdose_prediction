from flask import Flask, flash, request, redirect, url_for, render_template, jsonify, session
import pickle
import numpy as np
import pandas as pd
import os
import uuid
from werkzeug.utils import secure_filename
from flask_session import Session   # ✅ new import for persistent session

# ML models (imported but not directly used here)
from sklearn.ensemble import RandomForestClassifier, StackingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC

app = Flask(__name__)

# ----------------- Configuration -----------------
app.secret_key = os.urandom(24)   # ✅ secure random secret key
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'csv'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# ✅ Use filesystem session (important for Render)
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Create upload directory if it doesn't exist
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# ----------------- Helpers -----------------
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def Predict(L):
    filename = 'finalized_model.sav'   # Ensure this file exists in same folder as app.py
    loaded_model = pickle.load(open(filename, 'rb'))
    P = loaded_model.predict_proba(np.array([L]))
    print(P)
    print("Model Loaded Successfully")
    return P

# ----------------- Routes -----------------
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

# ✅ fixed route (both /Prediction and /prediction work)
@app.route("/Prediction", methods=["GET", "POST"])
@app.route("/prediction", methods=["GET", "POST"])
def Samples():
    if request.method == "POST":
        data = request.json
        print("Input Data:", data)
        R = list(Predict(data)[0])
        print("Prediction:", R)
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
                # Generate a unique filename
                filename = f"{uuid.uuid4().hex}_{secure_filename(file.filename)}"
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                
                # Validate CSV
                df = pd.read_csv(filepath)

                # ✅ Save to session
                session['uploaded_file'] = filename
                session['original_filename'] = file.filename
                session['columns'] = df.columns.tolist()
                session['row_count'] = len(df)
                session['preview_data'] = df.head(10).to_dict('records')

                print("Session before redirect:", dict(session))
                
                flash('File successfully uploaded', 'success')
                return redirect(url_for('preview'))
                
            except Exception as e:
                if os.path.exists(filepath):
                    os.remove(filepath)
                flash(f'Error processing file: {str(e)}', 'error')
                return redirect(request.url)
        else:
            flash('Invalid file type. Only CSV files are allowed.', 'error')
            return redirect(request.url)
    
    return render_template("upload.html")

@app.route("/preview", methods=["GET"])
def preview():
    if 'uploaded_file' not in session:
        flash('No file uploaded. Please upload a file first.', 'error')
        return redirect(url_for('upload'))
    
    filename = session.get('original_filename', 'Unknown')
    columns = session.get('columns', [])
    row_count = session.get('row_count', 0)
    preview_data = session.get('preview_data', [])

    print("Session at preview:", dict(session))
    
    return render_template("preview.html", 
                          filename=filename,
                          columns=columns,
                          row_count=row_count,
                          preview_data=preview_data)

@app.route("/chart")
def chart():
    return render_template("chart.html")

# ----------------- Run -----------------
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
