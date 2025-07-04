import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask
from flask_cors import CORS
from src.models.user import db
from src.routes.user import user_bp
from src.routes.chat import chat_bp
from src.routes.shopify import shopify_bp
from src.routes.training import training_bp

app = Flask(__name__)
app.config['SECRET_KEY'] = 'asdf#FGSgvasgf$5$WGT'

# --- CORRECT CORS CONFIGURATION ---
# Define all specific URLs that are allowed to make requests.
allowed_origins = [
    "https://feelori-admin-dashboard.onrender.com", # Your admin dashboard
    "https://feelori.com",                          # Your live website
    "http://localhost:5173"                         # For local testing
]
# Configure CORS to only allow requests from these specific origins.
CORS(app, origins=allowed_origins)
# --- END OF CORS CONFIGURATION ---

# Re-enable all your blueprints
app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(chat_bp, url_prefix='/api')
app.register_blueprint(shopify_bp, url_prefix='/api')
app.register_blueprint(training_bp, url_prefix='/api')

# Re-enable the database
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
with app.app_context():
    db.create_all()

@app.route('/')
def health_check():
    """A simple route for Render's health checks."""
    return "Backend is running with full logic!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)