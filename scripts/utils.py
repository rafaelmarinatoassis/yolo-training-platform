#!/usr/bin/env python3
"""
Utility scripts for YOLO Training Platform
"""

import os
import sys
import argparse
from app import create_app, db
from app.models import Dataset, Training, Test


def init_database():
    """Initialize the database with tables"""
    app = create_app()
    with app.app_context():
        db.create_all()
        print("Database initialized successfully!")


def cleanup_old_files():
    """Clean up old training and test files"""
    app = create_app()
    with app.app_context():
        # Find trainings marked as failed or canceled that are older than 7 days
        from datetime import datetime, timedelta
        
        old_date = datetime.utcnow() - timedelta(days=7)
        old_trainings = Training.query.filter(
            Training.status.in_(['failed', 'canceled']),
            Training.finished_at < old_date
        ).all()
        
        deleted_count = 0
        for training in old_trainings:
            if training.model_dir and os.path.exists(training.model_dir):
                import shutil
                shutil.rmtree(training.model_dir)
                deleted_count += 1
                print(f"Deleted training {training.id} files")
        
        print(f"Cleaned up {deleted_count} old training directories")


def backup_database():
    """Backup the SQLite database"""
    import shutil
    from datetime import datetime
    
    db_path = "yolo_trainer.db"
    if os.path.exists(db_path):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = f"backup_yolo_trainer_{timestamp}.db"
        shutil.copy2(db_path, backup_path)
        print(f"Database backed up to {backup_path}")
    else:
        print("Database file not found")


def list_datasets():
    """List all datasets in the system"""
    app = create_app()
    with app.app_context():
        datasets = Dataset.query.all()
        
        if not datasets:
            print("No datasets found")
            return
        
        print(f"Found {len(datasets)} datasets:")
        print("-" * 80)
        for dataset in datasets:
            print(f"ID: {dataset.id}")
            print(f"Name: {dataset.name}")
            print(f"Classes: {dataset.nc}")
            print(f"Path: {dataset.path}")
            print(f"Created: {dataset.created_at}")
            print("-" * 80)


def list_trainings():
    """List all trainings in the system"""
    app = create_app()
    with app.app_context():
        trainings = Training.query.all()
        
        if not trainings:
            print("No trainings found")
            return
        
        print(f"Found {len(trainings)} trainings:")
        print("-" * 80)
        for training in trainings:
            print(f"ID: {training.id}")
            print(f"Dataset: {training.dataset.name if training.dataset else 'Unknown'}")
            print(f"Status: {training.status}")
            print(f"Created: {training.created_at}")
            if training.started_at:
                print(f"Started: {training.started_at}")
            if training.finished_at:
                print(f"Finished: {training.finished_at}")
            print("-" * 80)


def check_system():
    """Check system requirements and dependencies"""
    print("Checking system requirements...")
    
    # Check Python version
    python_version = sys.version_info
    print(f"Python version: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    if python_version < (3, 10):
        print("WARNING: Python 3.10+ recommended")
    
    # Check required packages
    required_packages = [
        'flask', 'ultralytics', 'opencv-python', 'pillow', 
        'numpy', 'torch', 'torchvision'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✓ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"✗ {package} - MISSING")
    
    if missing_packages:
        print(f"\nInstall missing packages: pip install {' '.join(missing_packages)}")
    
    # Check GPU availability
    try:
        import torch
        if torch.cuda.is_available():
            print(f"✓ CUDA available - {torch.cuda.get_device_name(0)}")
        else:
            print("! CUDA not available - will use CPU")
    except ImportError:
        print("! PyTorch not installed")
    
    # Check disk space
    import shutil
    total, used, free = shutil.disk_usage(".")
    free_gb = free // (1024**3)
    print(f"Disk space: {free_gb}GB free")
    
    if free_gb < 10:
        print("WARNING: Low disk space (<10GB)")


def main():
    parser = argparse.ArgumentParser(description="YOLO Training Platform utilities")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Init database command
    subparsers.add_parser('init-db', help='Initialize the database')
    
    # Cleanup command
    subparsers.add_parser('cleanup', help='Clean up old files')
    
    # Backup command
    subparsers.add_parser('backup', help='Backup the database')
    
    # List commands
    subparsers.add_parser('list-datasets', help='List all datasets')
    subparsers.add_parser('list-trainings', help='List all trainings')
    
    # System check
    subparsers.add_parser('check-system', help='Check system requirements')
    
    args = parser.parse_args()
    
    if args.command == 'init-db':
        init_database()
    elif args.command == 'cleanup':
        cleanup_old_files()
    elif args.command == 'backup':
        backup_database()
    elif args.command == 'list-datasets':
        list_datasets()
    elif args.command == 'list-trainings':
        list_trainings()
    elif args.command == 'check-system':
        check_system()
    else:
        parser.print_help()


if __name__ == '__main__':
    main()