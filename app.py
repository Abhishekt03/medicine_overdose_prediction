from flask import Flask, flash, request, redirect, url_for, render_template, jsonify
import pickle
import numpy as np
import pandas as pd

# ML models (imported but not directly used here)
from sklearn.ensemble import RandomForestClassifier, StackingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC

app = Flask(__name__)

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

@app.route("/upload")
def upload():
    return render_template("upload.html")

# ✅ Fixed: allow both GET + POST for preview
@app.route("/preview", methods=["GET", "POST"])
def preview():
    if request.method == "POST":
        dataset = request.files["datasetfile"]
        df = pd.read_csv(dataset, encoding="unicode_escape")
        if "Id" in df.columns:   # Ensure column exists
            df.set_index("Id", inplace=True)
        return render_template("preview.html", df_view=df)
    # For GET, show empty preview page
    return render_template("preview.html", df_view=None)

@app.route("/chart")
def chart():
    return render_template("chart.html")

# ----------------- Run -----------------
if __name__ == "__main__":
    # Local run
    app.run(debug=True, host="0.0.0.0", port=5000)
