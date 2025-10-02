from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
import os
import threading
from datetime import datetime
from app import db
from app.models import Test, Training, Checkpoint
from app.services.infer import InferenceService
from app.services.storage import StorageService

tests_bp = Blueprint('tests', __name__)
inference = InferenceService()
storage = StorageService()


@tests_bp.route('/tests', methods=['GET'])
def list_tests():
    """List all tests with pagination"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    training_id = request.args.get('training_id', type=int)
    
    query = Test.query
    
    if training_id:
        query = query.filter(Test.training_id == training_id)
    
    tests = query.order_by(Test.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'tests': [test.to_dict() for test in tests.items],
        'total': tests.total,
        'pages': tests.pages,
        'current_page': page
    })


@tests_bp.route('/tests/<int:test_id>', methods=['GET'])
def get_test(test_id):
    """Get test details"""
    test = Test.query.get_or_404(test_id)
    
    test_dict = test.to_dict()
    
    # Add result files if available
    if test.result_dir and os.path.exists(test.result_dir):
        result_files = []
        for root, dirs, files in os.walk(test.result_dir):
            for file in files:
                if file.lower().endswith(('.jpg', '.jpeg', '.png', '.mp4', '.avi')):
                    rel_path = os.path.relpath(os.path.join(root, file), test.result_dir)
                    result_files.append(rel_path)
        test_dict['result_files'] = result_files
    
    return jsonify(test_dict)


@tests_bp.route('/api/tests/<int:test_id>', methods=['GET'])
def get_test_api(test_id):
    """Get test details via API"""
    return get_test(test_id)


@tests_bp.route('/tests', methods=['POST'])
def create_test():
    """Create a new test/inference job"""
    try:
        # Get form data
        training_id = request.form.get('training_id', type=int)
        model_path = request.form.get('model_path')  # Alternative to training_id
        source_type = request.form.get('source_type')  # image|video|dir|webcam
        
        if not source_type:
            return jsonify({'error': 'Source type is required'}), 400
        
        # Handle model file upload
        model_file = request.files.get('model_file')
        if model_file and model_file.filename:
            # Save uploaded model file
            filename = secure_filename(model_file.filename)
            if not filename.endswith('.pt'):
                return jsonify({'error': 'Model file must be a .pt file'}), 400
            
            # Create temporary directory for uploaded model
            import tempfile
            temp_dir = tempfile.mkdtemp()
            model_path = os.path.join(temp_dir, filename)
            model_file.save(model_path)
        
        # Determine model path
        if training_id:
            training = Training.query.get(training_id)
            if not training:
                return jsonify({'error': 'Training not found'}), 404
            
            if training.status != 'completed':
                return jsonify({'error': 'Training is not completed'}), 400
            
            # Get the best model
            best_checkpoint = Checkpoint.query.filter_by(
                training_id=training_id, is_final=True
            ).first()
            
            if not best_checkpoint:
                return jsonify({'error': 'Model file not found'}), 404
            
            model_path = best_checkpoint.file_path
        
        elif model_path:
            # Validate model path exists
            if not os.path.exists(model_path):
                return jsonify({'error': 'Model file not found'}), 404
        else:
            return jsonify({'error': 'Either training_id or model_path is required'}), 400
        
        # Create test record
        test = Test(
            training_id=training_id,
            source=source_type
        )
        db.session.add(test)
        db.session.flush()  # Get the ID
        
        # Create test directory
        test_dir = storage.create_test_directory(test.id)
        test.result_dir = test_dir
        
        input_path = None
        
        # Handle different source types
        if source_type == 'image':
            if 'image_file' not in request.files:
                return jsonify({'error': 'Image file is required'}), 400
            
            file = request.files['image_file']
            if file.filename == '':
                return jsonify({'error': 'No image file selected'}), 400
            
            # Save uploaded image
            filename = secure_filename(file.filename)
            input_path = os.path.join(test_dir, 'input_' + filename)
            file.save(input_path)
            test.input_path = input_path
            
        elif source_type == 'video':
            if 'video_file' not in request.files:
                return jsonify({'error': 'Video file is required'}), 400
            
            file = request.files['video_file']
            if file.filename == '':
                return jsonify({'error': 'No video file selected'}), 400
            
            # Save uploaded video
            filename = secure_filename(file.filename)
            input_path = os.path.join(test_dir, 'input_' + filename)
            file.save(input_path)
            test.input_path = input_path
            
        elif source_type == 'dir':
            if 'images_zip' not in request.files:
                return jsonify({'error': 'Images zip file is required'}), 400
            
            file = request.files['images_zip']
            if file.filename == '':
                return jsonify({'error': 'No zip file selected'}), 400
            
            # Save and extract zip
            filename = secure_filename(file.filename)
            zip_path = os.path.join(test_dir, filename)
            file.save(zip_path)
            
            # Extract images
            input_dir = os.path.join(test_dir, 'input_images')
            os.makedirs(input_dir, exist_ok=True)
            storage.extract_zip_to_directory(
                zip_path, input_dir, {'.jpg', '.jpeg', '.png', '.bmp'}
            )
            
            input_path = input_dir
            test.input_path = input_path
            os.remove(zip_path)  # Clean up zip file
            
        elif source_type == 'webcam':
            # Webcam doesn't need file upload
            test.input_path = 'webcam'
        
        db.session.commit()
        
        # Start inference in background
        thread = threading.Thread(
            target=_run_inference_async,
            args=(test.id, model_path, source_type, input_path)
        )
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'message': 'Test created and started',
            'test': test.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


def _run_inference_async(test_id, model_path, source_type, input_path):
    """Run inference asynchronously"""
    from app import create_app
    
    # Create application context for this thread
    app = create_app()
    with app.app_context():
        try:
            test = Test.query.get(test_id)
            if not test:
                return
            
            # Get inference parameters from request (you might want to store these in the test record)
            params = {
                'conf_threshold': 0.25,
                'iou_threshold': 0.45,
                'img_size': 640
            }
            
            # Run inference
            result = inference.run_inference(
                model_path, source_type, input_path, test_id, **params
            )
            
            # Update test record with results
            if result['success']:
                test.set_metrics(result.get('results', {}))
            else:
                test.set_metrics({'error': result.get('error', 'Unknown error')})
            
            db.session.commit()
            
        except Exception as e:
            print(f"Error in inference: {e}")
            # Update test with error
            try:
                test = Test.query.get(test_id)
                if test:
                    test.set_metrics({'error': str(e)})
                    db.session.commit()
            except Exception as db_error:
                print(f"Error updating test with error: {db_error}")


@tests_bp.route('/tests/<int:test_id>/results', methods=['GET'])
def get_test_results(test_id):
    """Get test results including annotated images/videos"""
    test = Test.query.get_or_404(test_id)
    
    if not test.result_dir or not os.path.exists(test.result_dir):
        return jsonify({'error': 'Results not available'}), 404
    
    results = {
        'test_id': test_id,
        'metrics': test.get_metrics(),
        'files': []
    }
    
    # List result files
    for root, dirs, files in os.walk(test.result_dir):
        for file in files:
            if file.lower().endswith(('.jpg', '.jpeg', '.png', '.mp4', '.avi')):
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, test.result_dir)
                
                # Generate URL for file access
                file_url = f'/api/files/tests/{test_id}/{rel_path}'
                
                results['files'].append({
                    'filename': file,
                    'path': rel_path,
                    'url': file_url,
                    'type': 'image' if file.lower().endswith(('.jpg', '.jpeg', '.png')) else 'video'
                })
    
    return jsonify(results)


@tests_bp.route('/api/tests/<int:test_id>/results', methods=['GET'])
def get_test_results_api(test_id):
    """Get test results via API"""
    return get_test_results(test_id)


@tests_bp.route('/tests/<int:test_id>', methods=['DELETE'])
def delete_test(test_id):
    """Delete a test and its results"""
    test = Test.query.get_or_404(test_id)
    
    try:
        # Delete result files
        if test.result_dir and os.path.exists(test.result_dir):
            storage.delete_test(test.result_dir)
        
        # Delete from database
        db.session.delete(test)
        db.session.commit()
        
        return jsonify({'message': 'Test deleted successfully'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# WebSocket endpoint for webcam inference
@tests_bp.route('/tests/webcam/frame', methods=['POST'])
def process_webcam_frame():
    """Process a single webcam frame"""
    try:
        data = request.get_json()
        
        model_path = data.get('model_path')
        frame_data = data.get('frame_data')  # Base64 encoded image
        
        if not model_path or not frame_data:
            return jsonify({'error': 'Model path and frame data are required'}), 400
        
        # Get inference parameters
        conf_threshold = data.get('conf_threshold', 0.25)
        iou_threshold = data.get('iou_threshold', 0.45)
        img_size = data.get('img_size', 640)
        
        # Process frame
        result = inference.process_webcam_frame(
            model_path, frame_data, conf_threshold, iou_threshold, img_size
        )
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500