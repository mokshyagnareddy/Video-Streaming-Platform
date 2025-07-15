# video_streaming_platform/app.py

import os
from flask import Flask, request, render_template, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename
import sqlite3

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Database setup
def init_db():
    with sqlite3.connect('videos.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS videos (
                          id INTEGER PRIMARY KEY AUTOINCREMENT,
                          filename TEXT NOT NULL)''')
        conn.commit()

init_db()

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    with sqlite3.connect('videos.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM videos')
        videos = cursor.fetchall()
    return render_template('index.html', videos=videos)

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return redirect(url_for('index'))
    file = request.files['file']
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        with sqlite3.connect('videos.db') as conn:
            cursor = conn.cursor()
            cursor.execute('INSERT INTO videos (filename) VALUES (?)', (filename,))
            conn.commit()

    return redirect(url_for('index'))

@app.route('/videos/<filename>')
def stream_video(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True)
