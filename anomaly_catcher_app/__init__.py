from flask import Flask, jsonify
import os 
import pathlib


app = Flask(__name__)

BASE_DIR = pathlib.Path(__file__).parent.resolve()

UPLOAD_FOLDER = BASE_DIR / 'uploads'
app.config['UPLOAD_FOLDER'] = str(UPLOAD_FOLDER)
app.config['MAX_CONTENT_LENGTH'] = 1 * 1024 * 1024 * 1024 

UPLOAD_FOLDER.mkdir(exist_ok=True, parents=True)

app.config['SECRET_KEY'] = 'my_secret_key'

from anomaly_catcher_app import routes

