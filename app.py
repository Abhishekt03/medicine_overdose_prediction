from flask import Flask, flash, request, redirect, url_for, render_template, jsonify, session
import pickle
import numpy as np
import pandas as pd
import os
import uuid
from werkzeug.utils import secure_filename

# ML models (imported but not directly used here)
from sklearn.ensemble import RandomForestClassifier, StackingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Add a secret key for session management

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'csv'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# Create upload directory if it doesn't exist
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ----------------- Prediction Function -----------------
def Predict(L):
    filename = 'finalized_model.sav'   # Make sure this file is in same folder as app.py
    loaded_model = pickle.load(open(filename, 'rb'))
    P = loaded_model.predict_proba(np.array([L]))
    print(P)
    print("Loaded Successfully")
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

@app.route("/Predict", methods=["GET", "POST"])
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
        # Check if the post request has the file part
        if 'datasetfile' not in request.files:
            flash('No file part', 'error')
            return redirect(request.url)
        
        file = request.files['datasetfile']
        
        # If user does not select file
        if file.filename == '':
            flash('No file selected', 'error')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            try:
                # Generate a unique filename to avoid conflicts
                filename = f"{uuid.uuid4().hex}_{secure_filename(file.filename)}"
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                
                # Try to read the CSV file to validate it
                df = pd.read_csv(filepath)
                
                # Store file info in session
                session['uploaded_file'] = filename
                session['original_filename'] = file.filename
                session['columns'] = df.columns.tolist()
                session['row_count'] = len(df)
                session['preview_data'] = df.head(10).to_dict('records')
                
                flash('File successfully uploaded', 'success')
                return redirect(url_for('preview'))
                
            except Exception as e:
                # Remove the file if there was an error
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
    # Check if a file has been uploaded
    if 'uploaded_file' not in session:
        flash('No file uploaded. Please upload a file first.', 'error')
        return redirect(url_for('upload'))
    
    # Get the data from session
    filename = session.get('original_filename', 'Unknown')
    columns = session.get('columns', [])
    row_count = session.get('row_count', 0)
    preview_data = session.get('preview_data', [])
    
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
    # Local run
    app.run(debug=True, host="0.0.0.0", port=5000)
