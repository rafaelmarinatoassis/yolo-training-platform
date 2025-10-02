from flask import Blueprint, request, jsonify, Response, send_file
from flask_socketio import emit, join_room, leave_room
import json
import os
from datetime import datetime
from app import db, socketio
from app.models import Training, TrainingMetric, Checkpoint, Dataset
from app.services.trainer import TrainingService
from app.services.storage import StorageService

trainings_bp = Blueprint('trainings', __name__)
storage = StorageService()
trainer = TrainingService(storage)


@trainings_bp.route('/trainings', methods=['GET'])
def list_trainings():
    """List all trainings with pagination"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    status_filter = request.args.get('status')
    dataset_id = request.args.get('dataset_id', type=int)
    
    query = Training.query
    
    if status_filter:
        query = query.filter(Training.status == status_filter)
    
    if dataset_id:
        query = query.filter(Training.dataset_id == dataset_id)
    
    trainings = query.order_by(Training.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'trainings': [training.to_dict() for training in trainings.items],
        'total': trainings.total,
        'pages': trainings.pages,
        'current_page': page
    })


@trainings_bp.route('/trainings/<int:training_id>', methods=['GET'])
def get_training(training_id):
    """Get training details"""
    training = Training.query.get_or_404(training_id)
    
    training_dict = training.to_dict()
    
    # Add latest metrics
    latest_metrics = TrainingMetric.query.filter_by(training_id=training_id)\
        .order_by(TrainingMetric.epoch.desc()).limit(10).all()
    training_dict['latest_metrics'] = [metric.to_dict() for metric in latest_metrics]
    
    # Add checkpoints
    checkpoints = Checkpoint.query.filter_by(training_id=training_id)\
        .order_by(Checkpoint.epoch.desc()).all()
    training_dict['checkpoints'] = [checkpoint.to_dict() for checkpoint in checkpoints]
    
    # Add current status
    status_info = trainer.get_training_status(training_id)
    training_dict.update(status_info)
    
    return jsonify(training_dict)


@trainings_bp.route('/trainings', methods=['POST'])
def create_training():
    """Create a new training job"""
    try:
        data = request.get_json()
        
        dataset_id = data.get('dataset_id')
        if not dataset_id:
            return jsonify({'error': 'Dataset ID is required'}), 400
        
        # Convert dataset_id to int
        try:
            dataset_id = int(dataset_id)
        except (ValueError, TypeError):
            return jsonify({'error': 'Invalid dataset ID'}), 400
        
        # Verify dataset exists
        dataset = Dataset.query.get(dataset_id)
        if not dataset:
            return jsonify({'error': 'Dataset not found'}), 404
        
        # Helper function to convert values
        def convert_to_bool(value):
            if isinstance(value, bool):
                return value
            if isinstance(value, str):
                return value.lower() in ('true', 'on', '1', 'yes')
            return bool(value)
        
        def convert_to_int(value, default):
            try:
                return int(value)
            except (ValueError, TypeError):
                return default
        
        def convert_to_float(value, default):
            try:
                return float(value)
            except (ValueError, TypeError):
                return default
        
        # Create training record
        training = Training(
            dataset_id=convert_to_int(dataset_id, 0),
            
            # Model configuration
            model_version=data.get('model_version', 'm'),
            task_type=data.get('task_type', 'detect'),
            device=data.get('device', 'auto'),
            
            # Training parameters
            epochs=convert_to_int(data.get('epochs', 100), 100),
            batch_size=convert_to_int(data.get('batch_size', 16), 16),
            img_size=convert_to_int(data.get('img_size', 640), 640),
            learning_rate=convert_to_float(data.get('lr', 0.01), 0.01),
            patience=convert_to_int(data.get('patience', 50), 50),
            workers=convert_to_int(data.get('workers', 8), 8),
            save_checkpoints=convert_to_bool(data.get('save_checkpoints', True)),
            use_augmentation=convert_to_bool(data.get('use_augmentation', True)),
            
            status='queued'
        )
        
        # Legacy config for backward compatibility
        config = {
            'epochs': training.epochs,
            'batch_size': training.batch_size,
            'img_size': training.img_size,
            'lr': training.learning_rate,
            'patience': training.patience,
            'workers': training.workers,
            'save_checkpoints': training.save_checkpoints,
            'use_augmentation': training.use_augmentation,
            'model_version': training.model_version,
            'task_type': training.task_type,
            'device': training.device
        }
        training.set_config(config)
        
        db.session.add(training)
        db.session.commit()
        
        # Start training asynchronously
        trainer.start_training(training.id)
        
        return jsonify({
            'success': True,
            'message': 'Training job created successfully',
            'training_id': training.id,
            'training': training.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@trainings_bp.route('/trainings/<int:training_id>/start', methods=['POST'])
def start_training(training_id):
    """Manually start a queued training"""
    training = Training.query.get_or_404(training_id)
    
    if training.status != 'queued':
        return jsonify({'error': 'Training is not in queued status'}), 400
    
    try:
        trainer.start_training(training_id)
        return jsonify({'message': 'Training started'})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@trainings_bp.route('/trainings/<int:training_id>/cancel', methods=['POST'])
def cancel_training(training_id):
    """Cancel an active training"""
    training = Training.query.get_or_404(training_id)
    
    if training.status not in ['queued', 'running']:
        return jsonify({'error': 'Training cannot be canceled'}), 400
    
    try:
        success = trainer.cancel_training(training_id)
        if success:
            return jsonify({'message': 'Training cancellation requested'})
        else:
            # If not in active trainings, update status directly
            training.status = 'canceled'
            training.finished_at = datetime.utcnow()
            db.session.commit()
            return jsonify({'message': 'Training canceled'})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@trainings_bp.route('/trainings/<int:training_id>/metrics', methods=['GET'])
def get_training_metrics(training_id):
    """Get training metrics with optional filtering"""
    training = Training.query.get_or_404(training_id)
    
    limit = request.args.get('limit', 100, type=int)
    
    metrics = TrainingMetric.query.filter_by(training_id=training_id)\
        .order_by(TrainingMetric.epoch.asc()).limit(limit).all()
    
    return jsonify({
        'metrics': [metric.to_dict() for metric in metrics],
        'total_count': len(training.metrics)
    })


@trainings_bp.route('/trainings/<int:training_id>/logs/stream', methods=['GET'])
def stream_training_logs(training_id):
    """Stream training logs via Server-Sent Events"""
    training = Training.query.get_or_404(training_id)
    
    def generate():
        # This is a simplified implementation
        # In a real scenario, you'd read from log files or queue
        yield f"data: Training {training_id} status: {training.status}\n\n"
        
        if training.status == 'completed':
            yield f"data: Training completed successfully\n\n"
        elif training.status == 'failed':
            yield f"data: Training failed\n\n"
        elif training.status == 'running':
            yield f"data: Training is currently running\n\n"
    
    return Response(generate(), mimetype='text/plain')


@trainings_bp.route('/trainings/<int:training_id>/download_model', methods=['GET'])
def download_model(training_id):
    """Download the trained model"""
    training = Training.query.get_or_404(training_id)
    
    if training.status != 'completed':
        return jsonify({'error': 'Training is not completed'}), 400
    
    # Find the best model file
    best_checkpoint = Checkpoint.query.filter_by(
        training_id=training_id, is_final=True
    ).first()
    
    if not best_checkpoint:
        return jsonify({'error': 'Model file not found'}), 404
    
    # In a real implementation, you'd send the file
    # For now, return the file path
    return jsonify({
        'download_url': f'/api/files/models/{training_id}/best.pt',
        'file_path': best_checkpoint.file_path
    })


@trainings_bp.route('/trainings/<int:training_id>', methods=['DELETE'])
def delete_training(training_id):
    """Delete a training and its artifacts"""
    training = Training.query.get_or_404(training_id)
    
    if training.status == 'running':
        return jsonify({'error': 'Cannot delete running training'}), 400
    
    try:
        # Cancel if queued
        if training.status == 'queued':
            trainer.cancel_training(training_id)
        
        # Delete model files and directories
        from app.services.storage import StorageService
        storage = StorageService()
        
        deleted_paths = []
        
        # Delete model directory if it exists
        if training.model_dir:
            try:
                storage.delete_training(training.model_dir)
                deleted_paths.append(training.model_dir)
            except Exception as e:
                print(f"Error deleting model directory {training.model_dir}: {e}")
        
        # Also try to delete by training ID path (fallback)
        try:
            fallback_path = os.path.join('data', 'models', str(training_id))
            if os.path.exists(fallback_path):
                storage.delete_training(fallback_path)
                deleted_paths.append(fallback_path)
        except Exception as e:
            print(f"Error deleting fallback path: {e}")
        
        # Delete from database (cascade will handle related records)
        db.session.delete(training)
        db.session.commit()
        
        message = 'Training deleted successfully'
        if deleted_paths:
            message += f'. Removed directories: {", ".join(deleted_paths)}'
        
        return jsonify({'message': message})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# WebSocket events for real-time updates
@socketio.on('connect', namespace='/ws/trainings')
def handle_connect():
    print('Client connected to training namespace')


@socketio.on('disconnect', namespace='/ws/trainings')
def handle_disconnect():
    print('Client disconnected from training namespace')


@socketio.on('join_training', namespace='/ws/trainings')
def handle_join_training(data):
    training_id = data.get('training_id')
    if training_id:
        join_room(f'training_{training_id}')
        emit('joined', {'training_id': training_id})


@socketio.on('leave_training', namespace='/ws/trainings')
def handle_leave_training(data):
    training_id = data.get('training_id')
    if training_id:
        leave_room(f'training_{training_id}')
        emit('left', {'training_id': training_id})


@trainings_bp.route('/trainings/<int:training_id>/files/<filename>')
def get_training_file(training_id, filename):
    """Serve training files (charts, images, etc.)"""
    training = Training.query.get_or_404(training_id)
    
    if not training.model_dir:
        return jsonify({'error': 'Training directory not found'}), 404
    
    # Security: only allow specific file types and names
    allowed_files = [
        'results.png', 'results.csv',
        'confusion_matrix.png', 'confusion_matrix_normalized.png',
        'F1_curve.png', 'P_curve.png', 'R_curve.png', 'PR_curve.png',
        'train_batch0.jpg', 'train_batch1.jpg', 'train_batch2.jpg',
        'val_batch0_labels.jpg', 'val_batch0_pred.jpg',
        'val_batch1_labels.jpg', 'val_batch1_pred.jpg',
        'labels.jpg', 'labels_correlogram.jpg'
    ]
    
    if filename not in allowed_files:
        return jsonify({'error': 'File not allowed'}), 403
    
    file_path = os.path.join(training.model_dir, 'run', filename)
    
    if not os.path.exists(file_path):
        return jsonify({'error': 'File not found'}), 404
    
    return send_file(file_path)


@trainings_bp.route('/trainings/<int:training_id>/files')
def list_training_files(training_id):
    """List available training files"""
    training = Training.query.get_or_404(training_id)
    
    if not training.model_dir:
        return jsonify({'files': []})
    
    run_dir = os.path.join(training.model_dir, 'run')
    if not os.path.exists(run_dir):
        return jsonify({'files': []})
    
    files = {}
    file_categories = {
        'metrics': ['results.png', 'F1_curve.png', 'P_curve.png', 'R_curve.png', 'PR_curve.png'],
        'confusion': ['confusion_matrix.png', 'confusion_matrix_normalized.png'],
        'training_samples': ['train_batch0.jpg', 'train_batch1.jpg', 'train_batch2.jpg'],
        'validation_samples': ['val_batch0_labels.jpg', 'val_batch0_pred.jpg', 'val_batch1_labels.jpg', 'val_batch1_pred.jpg'],
        'dataset_info': ['labels.jpg', 'labels_correlogram.jpg']
    }
    
    for category, filenames in file_categories.items():
        files[category] = []
        for filename in filenames:
            file_path = os.path.join(run_dir, filename)
            if os.path.exists(file_path):
                files[category].append({
                    'name': filename,
                    'url': f'/api/trainings/{training_id}/files/{filename}'
                })
    
    return jsonify({'files': files})


@trainings_bp.route('/trainings/<int:training_id>/csv-data', methods=['GET'])
def get_training_csv_data(training_id):
    """Get training metrics from results.csv file"""
    training = Training.query.get_or_404(training_id)
    
    # Build path to results.csv - use fallback if model_dir is None
    if training.model_dir:
        csv_path = os.path.join(training.model_dir, 'run', 'results.csv')
    else:
        # Fallback to standard path pattern (data/models/ID/run/results.csv)
        csv_path = os.path.join('data', 'models', str(training_id), 'run', 'results.csv')
    
    if not os.path.exists(csv_path):
        return jsonify({'error': f'Results CSV file not found at {csv_path}'}), 404
    
    try:
        import pandas as pd
        
        # Read CSV file
        df = pd.read_csv(csv_path)
        
        # Clean column names (remove extra whitespace)
        df.columns = df.columns.str.strip()
        
        # Convert to our metrics format
        metrics = []
        for _, row in df.iterrows():
            # Extract values with fallbacks for missing columns
            epoch = int(row.get('epoch', 0))
            
            # Use different possible column names for loss
            train_loss = row.get('train/box_loss', row.get('loss', 0))
            val_loss = row.get('val/box_loss', train_loss)
            
            # Use precision and recall as accuracy metrics
            precision = row.get('metrics/precision(B)', 0)
            recall = row.get('metrics/recall(B)', 0)
            
            # mAP metrics
            map50 = row.get('metrics/mAP50(B)', 0)
            map5095 = row.get('metrics/mAP50-95(B)', 0)
            
            metric = {
                'epoch': epoch,
                'loss': float(train_loss),
                'accuracy': float(recall),  # Use recall as main accuracy metric
                'val_loss': float(val_loss),
                'val_accuracy': float(precision),  # Use precision as validation accuracy
                'precision': float(precision),  # Add precision as separate field
                'recall': float(recall),        # Add recall as separate field
                'map50': float(map50),
                'map5095': float(map5095)
            }
            metrics.append(metric)
        
        return jsonify({
            'metrics': metrics,
            'total_epochs': len(metrics),
            'source': 'results.csv',
            'csv_path': csv_path
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to parse CSV: {str(e)}'}), 500