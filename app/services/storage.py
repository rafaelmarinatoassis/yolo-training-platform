import os
import shutil
import zipfile
from werkzeug.utils import secure_filename
from PIL import Image
import yaml


class StorageService:
    def __init__(self, data_root='data'):
        self.data_root = data_root
        self.datasets_dir = os.path.join(data_root, 'datasets')
        self.models_dir = os.path.join(data_root, 'models')
        self.tests_dir = os.path.join(data_root, 'tests')
        
        # Create directories if they don't exist
        os.makedirs(self.datasets_dir, exist_ok=True)
        os.makedirs(self.models_dir, exist_ok=True)
        os.makedirs(self.tests_dir, exist_ok=True)
    
    def create_dataset_structure(self, dataset_name):
        """Create the directory structure for a new dataset"""
        dataset_path = os.path.join(self.datasets_dir, secure_filename(dataset_name))
        
        # Create main dataset directory
        os.makedirs(dataset_path, exist_ok=True)
        
        # Create split directories
        for split in ['train', 'val', 'test']:
            os.makedirs(os.path.join(dataset_path, 'images', split), exist_ok=True)
            os.makedirs(os.path.join(dataset_path, 'labels', split), exist_ok=True)
        
        return dataset_path
    
    def extract_zip_to_directory(self, zip_file, destination_dir, allowed_extensions=None):
        """Extract zip file to destination directory with validation"""
        if allowed_extensions is None:
            allowed_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.txt'}
        
        extracted_files = []
        
        with zipfile.ZipFile(zip_file, 'r') as zip_ref:
            for file_info in zip_ref.infolist():
                # Skip directories
                if file_info.is_dir():
                    continue
                
                # Check file extension
                _, ext = os.path.splitext(file_info.filename.lower())
                if ext not in allowed_extensions:
                    continue
                
                # Extract file
                try:
                    zip_ref.extract(file_info, destination_dir)
                    extracted_files.append(os.path.join(destination_dir, file_info.filename))
                except Exception as e:
                    print(f"Error extracting {file_info.filename}: {e}")
        
        return extracted_files
    
    def validate_image(self, image_path):
        """Validate that the file is a valid image"""
        try:
            with Image.open(image_path) as img:
                img.verify()
            return True
        except Exception:
            return False
    
    def validate_yolo_label(self, label_path, num_classes):
        """Validate YOLO format label file"""
        try:
            with open(label_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    
                    parts = line.split()
                    if len(parts) != 5:
                        return False
                    
                    # Validate class index
                    class_idx = int(parts[0])
                    if class_idx < 0 or class_idx >= num_classes:
                        return False
                    
                    # Validate coordinates (should be normalized between 0 and 1)
                    for coord in parts[1:]:
                        val = float(coord)
                        if val < 0 or val > 1:
                            return False
            
            return True
        except Exception:
            return False
    
    def generate_dataset_yaml(self, dataset_path, dataset_name, classes):
        """Generate YOLO dataset.yaml file"""
        # Use absolute path to avoid confusion
        abs_dataset_path = os.path.abspath(dataset_path)
        
        yaml_content = {
            'path': abs_dataset_path,
            'train': 'images/train',
            'val': 'images/val', 
            'test': 'images/test',
            'nc': len(classes),
            'names': {i: name for i, name in enumerate(classes)}
        }
        
        yaml_file_path = os.path.join(dataset_path, 'dataset.yaml')
        with open(yaml_file_path, 'w') as f:
            yaml.dump(yaml_content, f, default_flow_style=False)
        
        return yaml_file_path
    
    def get_dataset_files_count(self, dataset_path):
        """Count files in each split of the dataset"""
        counts = {'train': 0, 'val': 0, 'test': 0}
        
        for split in counts.keys():
            images_dir = os.path.join(dataset_path, 'images', split)
            if os.path.exists(images_dir):
                counts[split] = len([f for f in os.listdir(images_dir) 
                                   if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp'))])
        
        return counts
    
    def create_training_directory(self, training_id):
        """Create directory for training outputs"""
        training_dir = os.path.join(self.models_dir, str(training_id))
        os.makedirs(training_dir, exist_ok=True)
        return training_dir
    
    def create_test_directory(self, test_id):
        """Create directory for test outputs"""
        test_dir = os.path.join(self.tests_dir, str(test_id))
        os.makedirs(test_dir, exist_ok=True)
        return test_dir
    
    def delete_dataset(self, dataset_path):
        """Delete dataset directory and all its contents"""
        try:
            if os.path.exists(dataset_path):
                print(f"Deleting dataset directory: {dataset_path}")
                shutil.rmtree(dataset_path)
                print(f"Successfully deleted dataset directory: {dataset_path}")
            else:
                print(f"Dataset directory not found: {dataset_path}")
        except Exception as e:
            print(f"Error deleting dataset directory {dataset_path}: {str(e)}")
            raise
    
    def delete_training(self, training_dir):
        """Delete training directory and all its contents"""
        try:
            if os.path.exists(training_dir):
                print(f"Deleting training directory: {training_dir}")
                shutil.rmtree(training_dir)
                print(f"Successfully deleted training directory: {training_dir}")
            else:
                print(f"Training directory not found: {training_dir}")
        except Exception as e:
            print(f"Error deleting training directory {training_dir}: {str(e)}")
            raise
    
    def delete_test(self, test_dir):
        """Delete test directory and all its contents"""
        if os.path.exists(test_dir):
            shutil.rmtree(test_dir)