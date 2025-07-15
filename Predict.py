from flask import Flask, flash, request, redirect, url_for,render_template,jsonify
import pickle
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.ensemble import StackingClassifier
import numpy as np

app = Flask(__name__)

def Predict(L):
    filename = 'finalized_model.sav'
    loaded_model = pickle.load(open(filename, 'rb'))

   # Keep only the first 22 features if you're adding more but keeping the model's expected number
    # Ensure L has 22 features
    P = loaded_model.predict_proba(np.array([L]))  # Now it has the correct shape

    print(P)
    print("Loaded Successfully")
    return P;

@app.route('/', methods = ['GET','POST'])
def Connect():
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

if __name__=="__main__":
	app.run(debug = True)