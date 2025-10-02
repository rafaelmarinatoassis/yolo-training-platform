from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO
from flask_cors import CORS
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Initialize extensions
db = SQLAlchemy()
socketio = SocketIO()

def create_app():
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///yolo_trainer.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['MAX_CONTENT_LENGTH'] = int(os.getenv('MAX_UPLOAD_SIZE', 2147483648))  # 2GB
    app.config['DATA_ROOT'] = os.getenv('DATA_ROOT', 'data')
    
    # Initialize extensions with app
    db.init_app(app)
    socketio.init_app(app, cors_allowed_origins="*", async_mode='eventlet')
    CORS(app)
    
    # Register blueprints
    from app.routes.ui import ui_bp
    from app.routes.datasets import datasets_bp
    from app.routes.trainings import trainings_bp
    
    app.register_blueprint(ui_bp)
    app.register_blueprint(datasets_bp, url_prefix='/api')
    app.register_blueprint(trainings_bp, url_prefix='/api')
    
    # Create database tables
    with app.app_context():
        from app.models import Dataset, Class, DatasetFile, Training, TrainingMetric, Checkpoint
        db.create_all()
    
    return app