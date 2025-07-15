from flask import Flask, flash, request, redirect, url_for,render_template,jsonify
import pickle
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.ensemble import StackingClassifier
import numpy as np
import flask
from flask import Flask, render_template, request
import pandas as pd


app = Flask(__name__)

def Predict(L):
    filename = 'finalized_model.sav'
    loaded_model = pickle.load(open(filename, 'rb'))

    P = loaded_model.predict_proba(np.array([L]))
    print(P)
    print("Loaded Successfully")
    return P;

@app.route("/")
def first():
  return render_template("first.html")
  
@app.route("/about")
def about():
  return render_template("about.html")


@app.route("/precautions")
def precautions():
  return render_template("precautions.html")



@app.route('/home', methods = ['GET','POST'])
def home():
    return render_template("home.html")
    


@app.route('/Predict', methods = ['GET','POST'])
def Samples():
    if request.method == 'POST':
        data = request.json
        print(data)
        R = list(Predict(data)[0]);
        print(R)
        print(type(R)) 
        return jsonify(R)

    # console.log(value);
    return render_template("home.html")


@app.route("/model")
def model():
  return render_template("model.html")

@app.route("/form", methods=['GET', 'POST'])
def form():
    return render_template('form.html')




@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/upload')
def upload():
    return render_template('upload.html')

@app.route('/preview',methods=["POST"])
def preview():
    if request.method == 'POST':
        dataset = request.files['datasetfile']
        df = pd.read_csv(dataset,encoding = 'unicode_escape')
        df.set_index('Id', inplace=True)
        return render_template("preview.html",df_view = df) 



@app.route('/chart')
def chart():
    return render_template('chart.html')

if __name__=="__main__":
	app.run(debug = True)