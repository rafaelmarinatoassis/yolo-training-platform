from threading import Thread
import os
import time
from datetime import datetime
from app.models import Training, Dataset, TrainingMetric, Checkpoint
from app import db, socketio


class TrainingService:
    def __init__(self, storage_service):
        self.storage = storage_service
        self.active_trainings = {}
    
    def start_training(self, training_id):
        """Start a new training process in a background thread"""
        if training_id in self.active_trainings:
            return False  # Training already running
        
        # Mark as active
        self.active_trainings[training_id] = {
            'thread': None,
            'canceled': False
        }
        
        # Start training thread
        thread = Thread(target=self._run_training, args=(training_id,))
        self.active_trainings[training_id]['thread'] = thread
        thread.start()
        
        return True
    
    def _run_training(self, training_id):
        """Run the actual training process"""
        from app import create_app
        
        # Create application context for this thread
        app = create_app()
        with app.app_context():
            training = None
            try:
                # Get training record
                training = Training.query.get(training_id)
                if not training:
                    return
                
                # Update status to running
                training.status = 'running'
                training.started_at = datetime.utcnow()
                db.session.commit()
                
                # Get dataset and validate
                dataset = Dataset.query.get(training.dataset_id)
                if not dataset:
                    raise ValueError("Dataset not found")
                
                # Create training directory
                import os
                training_dir = os.path.join(self.storage.models_dir, str(training.id))
                os.makedirs(training_dir, exist_ok=True)
                
                # Setup training configuration
                dataset_path = os.path.join(dataset.path, 'dataset.yaml')
                if not os.path.exists(dataset_path):
                    raise FileNotFoundError(f"Dataset YAML not found: {dataset_path}")

                # Configure YOLO model based on task type and version
                task_suffix = '' if training.task_type == 'detect' else f'-{training.task_type}'
                model_name = f"yolov8{training.model_version}{task_suffix}.pt"
                
                # Temporary workaround for PyTorch 2.6 weights_only issue
                import torch
                
                # Monkey patch torch.load to use weights_only=False during entire YOLO training process
                # This is needed for both model initialization and final model optimization
                original_torch_load = torch.load
                def patched_torch_load(*args, **kwargs):
                    kwargs.setdefault('weights_only', False)
                    return original_torch_load(*args, **kwargs)
                
                torch.load = patched_torch_load
                
                # Initialize YOLO model
                from ultralytics import YOLO
                model = YOLO(model_name)
                
                # Emit training started event
                socketio.emit('training_status', {
                    'training_id': training_id,
                    'status': 'running',
                    'message': f'Training started with YOLOv8{training.model_version} ({training.task_type})'
                }, namespace='/ws/trainings')
                
                # Emit training log
                socketio.emit('training_log', {
                    'training_id': training_id,
                    'timestamp': datetime.now().strftime('%H:%M:%S'),
                    'level': 'info',
                    'message': f'Iniciando treinamento do modelo YOLOv8{training.model_version}...'
                }, namespace='/ws/trainings')
                
                socketio.emit('training_log', {
                    'training_id': training_id,
                    'timestamp': datetime.now().strftime('%H:%M:%S'),
                    'level': 'info',
                    'message': f'Dataset: {training.dataset.name} | Épocas: {training.epochs} | Tamanho da imagem: {training.img_size}px'
                }, namespace='/ws/trainings')
                
                # Configure device based on selection
                device_config = training.device
                if device_config == 'auto':
                    # Let YOLO choose best available device
                    device_config = None
                elif device_config == 'cuda':
                    device_config = 0  # Use first GPU
                # For 'cpu' or 'mps', use the string as-is
                
                # Training arguments using specific fields
                train_args = {
                    'data': dataset_path,
                    'epochs': training.epochs,
                    'imgsz': training.img_size,
                    'batch': training.batch_size,
                    'lr0': training.learning_rate,
                    'patience': training.patience,
                    'workers': training.workers,
                    'save_period': 10 if training.save_checkpoints else -1,
                    'augment': training.use_augmentation,
                    'project': training_dir,
                    'name': 'run',
                    'exist_ok': True
                }
                
                # Add device only if specified
                if device_config is not None:
                    train_args['device'] = device_config
                
                # Custom callback for tracking progress
                def on_train_epoch_end(trainer):
                    if training_id in self.active_trainings and self.active_trainings[training_id].get('canceled', False):
                        raise KeyboardInterrupt("Training was canceled")
                    
                    # Get current epoch metrics
                    if hasattr(trainer, 'metrics') and trainer.metrics:
                        epoch = trainer.epoch + 1
                        
                        # Create metric record
                        metric = TrainingMetric(
                            training_id=training_id,
                            epoch=epoch,
                            loss=float(trainer.metrics.get('train/box_loss', 0)),
                            accuracy=float(trainer.metrics.get('metrics/mAP50', 0)),
                            val_loss=float(trainer.metrics.get('val/box_loss', 0)),
                            val_accuracy=float(trainer.metrics.get('val/mAP50', 0)),
                            map50=float(trainer.metrics.get('metrics/mAP50', 0)),
                            map=float(trainer.metrics.get('metrics/mAP50-95', 0))
                        )
                        db.session.add(metric)
                        db.session.commit()
                        
                        # Emit progress update
                        socketio.emit('training_progress', {
                            'training_id': training_id,
                            'epoch': epoch,
                            'total_epochs': training.epochs,
                            'loss': metric.loss,
                            'accuracy': metric.accuracy,
                            'val_loss': metric.val_loss,
                            'val_accuracy': metric.val_accuracy
                        }, namespace='/ws/trainings')
                        
                        # Emit detailed training log
                        socketio.emit('training_log', {
                            'training_id': training_id,
                            'timestamp': datetime.now().strftime('%H:%M:%S'),
                            'level': 'train',
                            'message': f'Época {epoch}/{training.epochs} - Loss: {metric.loss:.4f} | mAP50: {metric.map50:.2f}% | Accuracy: {metric.accuracy:.2f}%'
                        }, namespace='/ws/trainings')
                
                # Add callback to model
                model.add_callback('on_train_epoch_end', on_train_epoch_end)
                
                # Start training
                results = model.train(**train_args)
                
                # Training completed successfully
                training.status = 'completed'
                training.finished_at = datetime.utcnow()
                training.model_path = os.path.join(training_dir, 'run', 'weights', 'best.pt')
                training.model_dir = training_dir
                
                # Emit completion log
                socketio.emit('training_log', {
                    'training_id': training_id,
                    'timestamp': datetime.now().strftime('%H:%M:%S'),
                    'level': 'success',
                    'message': f'Treinamento concluído com sucesso! Modelo salvo em data/models/{training_id}/run/weights/'
                }, namespace='/ws/trainings')
                
                # Import metrics from results.csv
                self._import_results_csv(training_id, training_dir)
                
                # Save final checkpoint
                checkpoint = Checkpoint(
                    training_id=training_id,
                    epoch=training.epochs,
                    file_path=training.model_path,
                    is_final=True
                )
                db.session.add(checkpoint)
                db.session.commit()
                
                # Emit completion event
                socketio.emit('training_status', {
                    'training_id': training_id,
                    'status': 'completed',
                    'message': 'Training completed successfully'
                }, namespace='/ws/trainings')
                
            except KeyboardInterrupt:
                # Handle cancellation
                if training:
                    training.status = 'canceled'
                    training.finished_at = datetime.utcnow()
                    db.session.commit()
                
                socketio.emit('training_status', {
                    'training_id': training_id,
                    'status': 'canceled',
                    'message': 'Training was canceled'
                }, namespace='/ws/trainings')
                
            except Exception as e:
                print(f"DEBUG: Training error for ID {training_id}: {str(e)}")
                print(f"DEBUG: Error type: {type(e).__name__}")
                import traceback
                print(f"DEBUG: Traceback: {traceback.format_exc()}")
                
                # Handle errors
                if training:
                    training.status = 'failed'
                    training.finished_at = datetime.utcnow()
                    db.session.commit()

                socketio.emit('training_status', {
                    'training_id': training_id,
                    'status': 'failed',
                    'message': f'Training failed: {str(e)}'
                }, namespace='/ws/trainings')
                
            finally:
                # Restore original torch.load after training completes
                torch.load = original_torch_load
                
                # Clean up
                if training_id in self.active_trainings:
                    del self.active_trainings[training_id]
    
    def cancel_training(self, training_id):
        """Cancel an active training"""
        if training_id in self.active_trainings:
            self.active_trainings[training_id]['canceled'] = True
            return True
        return False
    
    def get_training_status(self, training_id):
        """Get the current status of a training"""
        training = Training.query.get(training_id)
        if not training:
            return None
        
        is_active = training_id in self.active_trainings
        
        return {
            'id': training.id,
            'status': training.status,
            'progress': self._calculate_progress(training),
            'is_active': is_active
        }
    
    def _calculate_progress(self, training):
        """Calculate training progress percentage"""
        if training.status in ['pending', 'failed']:
            return 0
        elif training.status == 'completed':
            return 100
        else:
            # Get latest metric to determine current epoch
            latest_metric = TrainingMetric.query.filter_by(training_id=training.id).order_by(TrainingMetric.epoch.desc()).first()
            if latest_metric and training.epochs > 0:
                return min(100, int((latest_metric.epoch / training.epochs) * 100))
            return 0
    
    def _import_results_csv(self, training_id, training_dir):
        """Import metrics from YOLO's results.csv file"""
        import pandas as pd
        import os
        
        results_path = os.path.join(training_dir, 'run', 'results.csv')
        if not os.path.exists(results_path):
            print(f"DEBUG: results.csv not found at {results_path}")
            return
        
        try:
            # Read CSV file and strip column names
            df = pd.read_csv(results_path)
            df.columns = df.columns.str.strip()  # Remove leading/trailing spaces
            print(f"DEBUG: Found {len(df)} epochs in results.csv")
            
            # Clear existing metrics to avoid duplicates
            TrainingMetric.query.filter_by(training_id=training_id).delete()
            
            # Import each epoch's metrics
            for _, row in df.iterrows():
                epoch = int(row.get('epoch', 0))
                
                metric = TrainingMetric(
                    training_id=training_id,
                    epoch=epoch,
                    loss=float(row.get('train/box_loss', 0)),
                    accuracy=float(row.get('metrics/mAP50(B)', 0)),
                    val_loss=float(row.get('val/box_loss', 0)),
                    val_accuracy=float(row.get('metrics/mAP50(B)', 0)),  # Using same as accuracy for now
                    map50=float(row.get('metrics/mAP50(B)', 0)),
                    map=float(row.get('metrics/mAP50-95(B)', 0))
                )
                db.session.add(metric)
            
            db.session.commit()
            print(f"DEBUG: Successfully imported {len(df)} metrics from results.csv")
            
        except Exception as e:
            print(f"DEBUG: Error importing results.csv: {e}")
            import traceback
            traceback.print_exc()