from datetime import datetime
from app import db
import json


class Dataset(db.Model):
    __tablename__ = 'datasets'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True, nullable=False)
    path = db.Column(db.String(500), nullable=False)
    nc = db.Column(db.Integer, default=0)
    yaml_file = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    classes = db.relationship('Class', backref='dataset', lazy=True, cascade='all, delete-orphan')
    files = db.relationship('DatasetFile', backref='dataset', lazy=True, cascade='all, delete-orphan')
    trainings = db.relationship('Training', back_populates='dataset', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'path': self.path,
            'nc': self.nc,
            'yaml_file': self.yaml_file,
            'created_at': self.created_at.isoformat(),
            'classes': [cls.to_dict() for cls in self.classes],
            'file_count': len(self.files)
        }


class Class(db.Model):
    __tablename__ = 'classes'
    
    id = db.Column(db.Integer, primary_key=True)
    dataset_id = db.Column(db.Integer, db.ForeignKey('datasets.id'), nullable=False)
    class_index = db.Column(db.Integer, nullable=False)
    class_name = db.Column(db.String(255), nullable=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'class_index': self.class_index,
            'class_name': self.class_name
        }


class DatasetFile(db.Model):
    __tablename__ = 'dataset_files'
    
    id = db.Column(db.Integer, primary_key=True)
    dataset_id = db.Column(db.Integer, db.ForeignKey('datasets.id'), nullable=False)
    split = db.Column(db.String(50), nullable=False)  # train|val|test
    file_path = db.Column(db.String(500), nullable=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'split': self.split,
            'file_path': self.file_path
        }


class Training(db.Model):
    __tablename__ = 'trainings'
    
    id = db.Column(db.Integer, primary_key=True)
    dataset_id = db.Column(db.Integer, db.ForeignKey('datasets.id'), nullable=False)
    
    # Model configuration
    model_version = db.Column(db.String(10), default='m')  # n, s, m, l, x
    task_type = db.Column(db.String(20), default='detect')  # detect, classify, segment, pose
    device = db.Column(db.String(20), default='auto')  # auto, cuda, mps, cpu
    
    # Training parameters
    epochs = db.Column(db.Integer, default=100)
    batch_size = db.Column(db.Integer, default=16)
    img_size = db.Column(db.Integer, default=640)
    learning_rate = db.Column(db.Float, default=0.01)
    patience = db.Column(db.Integer, default=50)
    workers = db.Column(db.Integer, default=8)
    save_checkpoints = db.Column(db.Boolean, default=True)
    use_augmentation = db.Column(db.Boolean, default=True)
    
    # Legacy config field (for backward compatibility)
    config_json = db.Column(db.Text)
    
    # Status and timestamps
    status = db.Column(db.String(50), nullable=False, default='queued')  # queued|running|completed|failed|canceled
    started_at = db.Column(db.DateTime)
    finished_at = db.Column(db.DateTime)
    model_dir = db.Column(db.String(500))
    model_path = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    dataset = db.relationship('Dataset', back_populates='trainings')
    metrics = db.relationship('TrainingMetric', backref='training', lazy=True, cascade='all, delete-orphan')
    checkpoints = db.relationship('Checkpoint', back_populates='training', lazy=True, cascade='all, delete-orphan')
    tests = db.relationship('Test', back_populates='training', lazy=True)
    
    def get_config(self):
        return json.loads(self.config_json) if self.config_json else {}
    
    def set_config(self, config_dict):
        self.config_json = json.dumps(config_dict)
    
    def to_dict(self):
        return {
            'id': self.id,
            'dataset_id': self.dataset_id,
            'dataset_name': self.dataset.name if self.dataset else None,
            
            # Model configuration
            'model_version': self.model_version,
            'task_type': self.task_type,
            'device': self.device,
            
            # Training parameters
            'epochs': self.epochs,
            'batch_size': self.batch_size,
            'img_size': self.img_size,
            'learning_rate': self.learning_rate,
            'patience': self.patience,
            'workers': self.workers,
            'save_checkpoints': self.save_checkpoints,
            'use_augmentation': self.use_augmentation,
            
            # Legacy config for backward compatibility
            'config': self.get_config(),
            
            # Status and paths
            'status': self.status,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'finished_at': self.finished_at.isoformat() if self.finished_at else None,
            'model_dir': self.model_dir,
            'model_path': self.model_path,
            'created_at': self.created_at.isoformat(),
            
            # Relationships
            'metrics_count': len(self.metrics),
            'checkpoints_count': len(self.checkpoints)
        }


class TrainingMetric(db.Model):
    __tablename__ = 'training_metrics'
    
    id = db.Column(db.Integer, primary_key=True)
    training_id = db.Column(db.Integer, db.ForeignKey('trainings.id'), nullable=False)
    epoch = db.Column(db.Integer)
    step = db.Column(db.Integer)
    loss = db.Column(db.Float)
    accuracy = db.Column(db.Float)
    val_loss = db.Column(db.Float)
    val_accuracy = db.Column(db.Float)
    map50 = db.Column(db.Float)
    map = db.Column(db.Float)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'epoch': self.epoch,
            'step': self.step,
            'loss': self.loss,
            'accuracy': self.accuracy,
            'val_loss': self.val_loss,
            'val_accuracy': self.val_accuracy,
            'map50': self.map50,
            'map': self.map,
            'timestamp': self.timestamp.isoformat()
        }


class Checkpoint(db.Model):
    __tablename__ = 'checkpoints'
    
    id = db.Column(db.Integer, primary_key=True)
    training_id = db.Column(db.Integer, db.ForeignKey('trainings.id'), nullable=False)
    epoch = db.Column(db.Integer)
    file_path = db.Column(db.String(500))
    is_final = db.Column(db.Boolean, default=False)
    
    # Relationships
    training = db.relationship('Training', back_populates='checkpoints')
    
    def to_dict(self):
        return {
            'id': self.id,
            'epoch': self.epoch,
            'file_path': self.file_path,
            'is_final': self.is_final
        }


class Test(db.Model):
    __tablename__ = 'tests'
    
    id = db.Column(db.Integer, primary_key=True)
    training_id = db.Column(db.Integer, db.ForeignKey('trainings.id'), nullable=True)  # Permitir None para testes diretos
    source = db.Column(db.String(50), nullable=False)  # image|video|dir|webcam
    input_path = db.Column(db.String(500))
    result_dir = db.Column(db.String(500))
    metrics_json = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    training = db.relationship('Training', back_populates='tests')
    
    def get_metrics(self):
        return json.loads(self.metrics_json) if self.metrics_json else {}
    
    def set_metrics(self, metrics_dict):
        self.metrics_json = json.dumps(metrics_dict)
    
    def to_dict(self):
        return {
            'id': self.id,
            'training_id': self.training_id,
            'source': self.source,
            'input_path': self.input_path,
            'result_dir': self.result_dir,
            'metrics': self.get_metrics(),
            'created_at': self.created_at.isoformat()
        }