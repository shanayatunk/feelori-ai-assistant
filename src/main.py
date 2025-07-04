# src/main.py
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask
from flask_cors import CORS
from src.routes.training import training_bp # We only need the training blueprint for this test

app = Flask(__name__)

# Define allowed origins
allowed_origins = [
    "https://feelori-admin-dashboard.onrender.com",
    "https://feelori.com",
    "http://localhost:5173"
]

CORS(app, origins=allowed_origins)

# Register only the training blueprint
app.register_blueprint(training_bp, url_prefix='/api')

@app.route('/')
def health_check():
    return "Backend is running!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)