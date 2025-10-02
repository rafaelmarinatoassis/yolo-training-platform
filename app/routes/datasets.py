from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
import os
import json
from app import db
from app.models import Dataset, Class, DatasetFile
from app.services.storage import StorageService

datasets_bp = Blueprint('datasets', __name__)
storage = StorageService()


@datasets_bp.route('/datasets', methods=['GET'])
def list_datasets():
    """List all datasets with pagination"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    datasets = Dataset.query.paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'datasets': [dataset.to_dict() for dataset in datasets.items],
        'total': datasets.total,
        'pages': datasets.pages,
        'current_page': page
    })


@datasets_bp.route('/datasets/<int:dataset_id>', methods=['GET'])
def get_dataset(dataset_id):
    """Get dataset details"""
    dataset = Dataset.query.get_or_404(dataset_id)
    
    # Get file counts
    file_counts = storage.get_dataset_files_count(dataset.path)
    
    dataset_dict = dataset.to_dict()
    dataset_dict['file_counts'] = file_counts
    
    return jsonify(dataset_dict)


@datasets_bp.route('/datasets', methods=['POST'])
def create_dataset():
    """Create a new dataset"""
    try:
        # Get form data
        name = request.form.get('name')
        classes_json = request.form.get('classes')
        
        if not name or not classes_json:
            return jsonify({'error': 'Name and classes are required'}), 400
        
        # Parse classes
        try:
            classes = json.loads(classes_json)
        except json.JSONDecodeError:
            return jsonify({'error': 'Invalid classes JSON format'}), 400
        
        # Check if dataset name already exists
        existing = Dataset.query.filter_by(name=name).first()
        if existing:
            return jsonify({'error': 'Dataset name already exists'}), 400
        
        # Create dataset directory structure
        dataset_path = storage.create_dataset_structure(name)
        
        # Create dataset record
        dataset = Dataset(
            name=name,
            path=dataset_path,
            nc=len(classes)
        )
        db.session.add(dataset)
        db.session.flush()  # Get the ID
        
        # Add classes
        for i, class_name in enumerate(classes):
            class_obj = Class(
                dataset_id=dataset.id,
                class_index=i,
                class_name=class_name
            )
            db.session.add(class_obj)
        
        # Process uploaded files
        uploaded_files = []
        print(f"DEBUG: Processing files for dataset {name}")
        print(f"DEBUG: request.files keys: {list(request.files.keys())}")
        
        for split in ['train', 'val', 'test']:
            # Process images (multiple files)
            images_key = f'{split}_images'
            print(f"DEBUG: Looking for {images_key}")
            if images_key in request.files:
                files = request.files.getlist(images_key)
                print(f"DEBUG: Found {len(files)} files for {images_key}")
                for file in files:
                    if file.filename:
                        print(f"DEBUG: Processing image file: {file.filename}")
                        filename = secure_filename(file.filename)
                        images_dir = os.path.join(dataset_path, 'images', split)
                        os.makedirs(images_dir, exist_ok=True)
                        
                        file_path = os.path.join(images_dir, filename)
                        file.save(file_path)
                        print(f"DEBUG: Saved image to: {file_path}")
                        
                        # Validate image
                        if storage.validate_image(file_path):
                            uploaded_files.append(file_path)
                            print(f"DEBUG: Image validation passed: {file_path}")
                            # Record in database
                            dataset_file = DatasetFile(
                                dataset_id=dataset.id,
                                split=split,
                                file_path=file_path
                            )
                            db.session.add(dataset_file)
                        else:
                            print(f"DEBUG: Image validation failed, removing: {file_path}")
                            os.remove(file_path)  # Remove invalid files
                    else:
                        print(f"DEBUG: Empty filename for {images_key}")
            else:
                print(f"DEBUG: No files found for {images_key}")
            
            # Process labels (multiple files)
            labels_key = f'{split}_labels'
            print(f"DEBUG: Looking for {labels_key}")
            if labels_key in request.files:
                files = request.files.getlist(labels_key)
                print(f"DEBUG: Found {len(files)} files for {labels_key}")
                for file in files:
                    if file.filename:
                        print(f"DEBUG: Processing label file: {file.filename}")
                        filename = secure_filename(file.filename)
                        labels_dir = os.path.join(dataset_path, 'labels', split)
                        os.makedirs(labels_dir, exist_ok=True)
                        
                        file_path = os.path.join(labels_dir, filename)
                        file.save(file_path)
                        print(f"DEBUG: Saved label to: {file_path}")
                        
                        # Validate label
                        if storage.validate_yolo_label(file_path, len(classes)):
                            uploaded_files.append(file_path)
                            print(f"DEBUG: Label validation passed: {file_path}")
                            # Record in database
                            dataset_file = DatasetFile(
                                dataset_id=dataset.id,
                                split=split,
                                file_path=file_path
                            )
                            db.session.add(dataset_file)
                        else:
                            print(f"DEBUG: Label validation failed, removing: {file_path}")
                            os.remove(file_path)  # Remove invalid files
                    else:
                        print(f"DEBUG: Empty filename for {labels_key}")
            else:
                print(f"DEBUG: No files found for {labels_key}")
        
        print(f"DEBUG: Total uploaded files: {len(uploaded_files)}")
        
        # Generate YAML file
        yaml_file = storage.generate_dataset_yaml(dataset_path, name, classes)
        dataset.yaml_file = yaml_file
        
        # Commit all changes
        db.session.commit()
        
        return jsonify({
            'message': 'Dataset created successfully',
            'dataset': dataset.to_dict(),
            'uploaded_files_count': len(uploaded_files)
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@datasets_bp.route('/datasets/<int:dataset_id>', methods=['PUT'])
def update_dataset(dataset_id):
    """Update dataset information"""
    dataset = Dataset.query.get_or_404(dataset_id)
    
    try:
        data = request.get_json()
        
        # Update basic info
        if 'name' in data:
            # Check for name conflicts
            existing = Dataset.query.filter(
                Dataset.name == data['name'],
                Dataset.id != dataset_id
            ).first()
            if existing:
                return jsonify({'error': 'Dataset name already exists'}), 400
            dataset.name = data['name']
        
        # Update classes
        if 'classes' in data:
            # Delete existing classes
            Class.query.filter_by(dataset_id=dataset_id).delete()
            
            # Add new classes
            classes = data['classes']
            for i, class_name in enumerate(classes):
                class_obj = Class(
                    dataset_id=dataset_id,
                    class_index=i,
                    class_name=class_name
                )
                db.session.add(class_obj)
            
            dataset.nc = len(classes)
            
            # Regenerate YAML
            yaml_file = storage.generate_dataset_yaml(
                dataset.path, dataset.name, classes
            )
            dataset.yaml_file = yaml_file
        
        db.session.commit()
        
        return jsonify({
            'message': 'Dataset updated successfully',
            'dataset': dataset.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@datasets_bp.route('/datasets/<int:dataset_id>', methods=['DELETE'])
def delete_dataset(dataset_id):
    """Delete a dataset"""
    dataset = Dataset.query.get_or_404(dataset_id)
    
    try:
        # Check if dataset has trainings
        if dataset.trainings:
            return jsonify({
                'error': 'Cannot delete dataset with existing trainings'
            }), 400
        
        # Delete files from disk
        storage.delete_dataset(dataset.path)
        
        # Delete from database (cascade will handle related records)
        db.session.delete(dataset)
        db.session.commit()
        
        return jsonify({'message': 'Dataset deleted successfully'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@datasets_bp.route('/datasets/<int:dataset_id>/yaml', methods=['GET'])
def get_dataset_yaml(dataset_id):
    """Get dataset YAML content"""
    dataset = Dataset.query.get_or_404(dataset_id)
    
    if not dataset.yaml_file or not os.path.exists(dataset.yaml_file):
        return jsonify({'error': 'YAML file not found'}), 404
    
    try:
        with open(dataset.yaml_file, 'r') as f:
            yaml_content = f.read()
        
        return jsonify({
            'yaml_content': yaml_content,
            'file_path': dataset.yaml_file
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@datasets_bp.route('/datasets/<int:dataset_id>/yaml', methods=['PUT'])
def update_dataset_yaml(dataset_id):
    """Update dataset YAML content"""
    dataset = Dataset.query.get_or_404(dataset_id)
    
    try:
        data = request.get_json()
        yaml_content = data.get('yaml_content')
        
        if not yaml_content:
            return jsonify({'error': 'YAML content is required'}), 400
        
        # Save YAML content
        with open(dataset.yaml_file, 'w') as f:
            f.write(yaml_content)
        
        return jsonify({'message': 'YAML updated successfully'})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500