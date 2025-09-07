from flask import Flask, render_template, request, redirect, url_for, flash, send_file
import pandas as pd
import os
import io
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-in-production'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB limit
app.config['ALLOWED_EXTENSIONS'] = {'csv'}

# Create upload directory if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/prediction')
def prediction():
    # Add your prediction logic here
    return render_template('prediction.html')

@app.route('/precautions')
def precautions():
    return render_template('precautions.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # Check if the post request has the file part
        if 'datasetfile' not in request.files:
            flash('No file part in the request', 'error')
            return redirect(request.url)
        
        file = request.files['datasetfile']
        
        # If user does not select file, browser submits empty part
        if file.filename == '':
            flash('No file selected', 'error')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Store filename in session for later use
            session['uploaded_filename'] = filename
            
            # Redirect to preview page
            return redirect(url_for('preview'))
        else:
            flash('Invalid file type. Only CSV files are allowed.', 'error')
    
    return render_template('upload.html')

@app.route('/preview')
def preview():
    # Check if a file has been uploaded
    if 'uploaded_filename' not in session:
        flash('Please upload a file first', 'error')
        return redirect(url_for('upload_file'))
    
    filename = session['uploaded_filename']
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
    # Read the CSV file for preview
    try:
        df = pd.read_csv(filepath)
        df_view = df.head(10)  # Preview first 10 rows
        return render_template('preview.html', 
                              df_view=df_view.to_html(classes='table table-striped', index=False),
                              filename=filename)
    except Exception as e:
        flash(f'Error reading CSV file: {str(e)}', 'error')
        return redirect(url_for('upload_file'))

@app.route('/train', methods=['POST'])
def train_model():
    # Check if a file has been uploaded
    if 'uploaded_filename' not in session:
        flash('Please upload a file first', 'error')
        return redirect(url_for('upload_file'))
    
    filename = session['uploaded_filename']
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
    # Add your model training logic here
    try:
        df = pd.read_csv(filepath)
        # Your training code would go here
        
        flash('Model training completed successfully!', 'success')
        return redirect(url_for('prediction'))
    except Exception as e:
        flash(f'Error during training: {str(e)}', 'error')
        return redirect(url_for('preview'))

# Add a sample route for prediction page
@app.route('/prediction')
def prediction_page():
    return render_template('prediction.html', prediction_result=None)

if __name__ == '__main__':
    app.secret_key = 'your-secret-key-change-in-production'
    app.run(debug=True)
