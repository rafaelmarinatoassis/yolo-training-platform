from flask import Blueprint, render_template, send_from_directory, current_app
import os
from app.models import Training, Dataset, TrainingMetric
from app import db

ui_bp = Blueprint('ui', __name__)


@ui_bp.route('/')
def index():
    return render_template('index.html')


@ui_bp.route('/datasets')
def datasets_page():
    return render_template('datasets.html')


@ui_bp.route('/datasets/create')
def create_dataset_page():
    return render_template('create_dataset.html')


@ui_bp.route('/train')
def train_page():
    return render_template('train.html')


@ui_bp.route('/trainings')
def trainings_page():
    return render_template('trainings.html')


@ui_bp.route('/training/<int:training_id>')
def training_details_page(training_id):
    training = Training.query.get_or_404(training_id)
    
    metrics = TrainingMetric.query.filter_by(training_id=training_id).order_by(TrainingMetric.epoch.desc()).limit(10).all()
    
    current_epoch = 0
    if metrics:
        current_epoch = metrics[0].epoch
    
    progress = 0
    if training.epochs > 0:
        progress = int((current_epoch / training.epochs) * 100)
    
    duration = None
    if training.started_at:
        if training.finished_at:
            duration_seconds = (training.finished_at - training.started_at).total_seconds()
        else:
            from datetime import datetime
            duration_seconds = (datetime.utcnow() - training.started_at).total_seconds()
        
        hours = int(duration_seconds // 3600)
        minutes = int((duration_seconds % 3600) // 60)
        if hours > 0:
            duration = f"{hours}h {minutes}m"
        else:
            duration = f"{minutes}m"
    
    elapsed_time = duration or '-'
    estimated_time = '-'
    processing_speed = '-'
    
    if training.started_at and current_epoch > 0:
        from datetime import datetime
        elapsed_seconds = (datetime.utcnow() - training.started_at).total_seconds()
        time_per_epoch = elapsed_seconds / current_epoch
        remaining_epochs = training.epochs - current_epoch
        
        if remaining_epochs > 0:
            remaining_seconds = remaining_epochs * time_per_epoch
            est_hours = int(remaining_seconds // 3600)
            est_minutes = int((remaining_seconds % 3600) // 60)
            if est_hours > 0:
                estimated_time = f"{est_hours}h {est_minutes}m"
            else:
                estimated_time = f"{est_minutes}m"
        
        processing_speed = f"{time_per_epoch:.1f}s/época"
    
    return render_template('training_dashboard.html',
                         training=training,
                         training_id=training_id,
                         current_epoch=current_epoch,
                         progress=progress,
                         duration=duration,
                         elapsed_time=elapsed_time,
                         estimated_time=estimated_time,
                         processing_speed=processing_speed,
                         latest_metrics=metrics)


@ui_bp.route('/training/<int:training_id>/details')
def training_details_original(training_id):
    """Training details original page (without dashboard)"""
    training = Training.query.get_or_404(training_id)
    
    # Get training metrics
    metrics = TrainingMetric.query.filter_by(training_id=training_id)\
        .order_by(TrainingMetric.epoch.desc()).limit(10).all()
    
    # Calculate current epoch
    current_epoch = 0
    if metrics:
        current_epoch = metrics[0].epoch
    
    # Calculate progress percentage
    progress = 0
    if training.epochs > 0:
        progress = int((current_epoch / training.epochs) * 100)
    
    # Calculate duration
    duration = None
    if training.started_at:
        if training.finished_at:
            duration_seconds = (training.finished_at - training.started_at).total_seconds()
        else:
            from datetime import datetime
            duration_seconds = (datetime.utcnow() - training.started_at).total_seconds()
        
        hours = int(duration_seconds // 3600)
        minutes = int((duration_seconds % 3600) // 60)
        if hours > 0:
            duration = f"{hours}h {minutes}m"
        else:
            duration = f"{minutes}m"
    
    # Additional timing calculations
    elapsed_time = duration or '-'
    estimated_time = '-'
    processing_speed = '-'
    
    if training.started_at and current_epoch > 0:
        from datetime import datetime
        elapsed_seconds = (datetime.utcnow() - training.started_at).total_seconds()
        time_per_epoch = elapsed_seconds / current_epoch
        remaining_epochs = training.epochs - current_epoch
        
        if remaining_epochs > 0:
            remaining_seconds = remaining_epochs * time_per_epoch
            est_hours = int(remaining_seconds // 3600)
            est_minutes = int((remaining_seconds % 3600) // 60)
            if est_hours > 0:
                estimated_time = f"{est_hours}h {est_minutes}m"
            else:
                estimated_time = f"{est_minutes}m"
        
        processing_speed = f"{time_per_epoch:.1f}s/época"
    
    return render_template('training_details.html',
                         training=training,
                         training_id=training_id,
                         current_epoch=current_epoch,
                         progress=progress,
                         duration=duration,
                         elapsed_time=elapsed_time,
                         estimated_time=estimated_time,
                         processing_speed=processing_speed,
                         latest_metrics=metrics)


@ui_bp.route('/files/<int:training_id>/<filename>')
def serve_training_file(training_id, filename):
    data_root = current_app.config.get('DATA_ROOT', 'data')
    model_dir = os.path.join(data_root, 'models', str(training_id))
    return send_from_directory(model_dir, filename)
