import os
from flask import (
    Flask, flash, request, redirect, url_for,
    send_from_directory, render_template_string
)
from werkzeug.utils import secure_filename
from pathlib import Path

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Needed for flash messages

# Constants
BASE_UPLOAD_DIR = "./backups"
app.config['MAX_CONTENT_LENGTH'] = 64 * 1024 * 1024  # Max file size for transfer

# Ensure base backup directory exists
os.makedirs(BASE_UPLOAD_DIR, exist_ok=True)

# Renders the homepage with inline HTML
@app.route('/')
def index():
    student_ip = request.remote_addr
    student_dir = os.path.join(BASE_UPLOAD_DIR, student_ip)
    os.makedirs(student_dir, exist_ok=True)

    # Get the list of files in the student's directory
    files = [file.name for file in Path(student_dir).glob('*')]
    
    return render_template_string('''
        <!doctype html>
        <title>CybrShare - Home</title>
        <h1><b>CybrShare</b></h1>
        <h2> --- Upload --- </h2>
        <p>Upload Size Limit: {{ config['MAX_CONTENT_LENGTH'] }} bytes</p>
        <form method="post" enctype="multipart/form-data" action="{{ url_for('upload_file') }}">
            <input type="file" name="file">
            <input type="submit" value="Upload">
        </form>
        
        <h2> --- Download --- </h2>
        <form action="{{ url_for('download') }}" method="post">
            <select name="file">
                {% for datam in files %}
                    <option value="{{datam}}">{{datam}}</option>
                {% endfor %}
            </select>
            <input type="submit" value="Download Selected File">
        </form>
    ''', files=files)

# Handles file uploads
@app.route('/', methods=['POST'])
def upload_file():
    student_ip = request.remote_addr
    student_dir = os.path.join(BASE_UPLOAD_DIR, student_ip)
    os.makedirs(student_dir, exist_ok=True)

    if 'file' not in request.files:
        flash('No file part')
        return redirect(url_for('index'))

    file = request.files['file']
    if file.filename == '':
        flash('No selected file')
        return redirect(url_for('index'))

    if file:
        filename = secure_filename(file.filename)
        save_path = os.path.join(student_dir, filename)
        file.save(save_path)
        print(f"File saved: {save_path}")
        return redirect(url_for('index'))  # Redirect to the index after upload

# Handles file download
@app.route('/download', methods=['POST'])
def download():
    student_ip = request.remote_addr
    student_dir = os.path.join(BASE_UPLOAD_DIR, student_ip)
    os.makedirs(student_dir, exist_ok=True)

    # Get the filename from the form submission
    filename = request.form.get('file')
    
    if filename:
        # Ensure the file exists before attempting to send it
        file_path = os.path.join(student_dir, filename)
        if os.path.exists(file_path):
            return send_from_directory(student_dir, filename)
        else:
            flash("File not found.")
            return redirect(url_for('index'))
    else:
        flash("No file selected.")
        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)

