import os
import cv2
import numpy as np
from ultralytics import YOLO
from PIL import Image
import json
from app.services.storage import StorageService


class InferenceService:
    def __init__(self):
        self.storage = StorageService()
    
    def run_inference(self, model_path, source_type, input_path, test_id, **kwargs):
        """Run inference on given input"""
        try:
            # Create test directory
            test_dir = self.storage.create_test_directory(test_id)
            
            # Load model
            model = YOLO(model_path)
            
            # Set inference parameters
            conf_threshold = kwargs.get('conf_threshold', 0.25)
            iou_threshold = kwargs.get('iou_threshold', 0.45)
            img_size = kwargs.get('img_size', 640)
            
            results = []
            output_paths = []
            
            if source_type == 'image':
                results = self._process_image(model, input_path, test_dir, conf_threshold, iou_threshold, img_size)
            elif source_type == 'video':
                results = self._process_video(model, input_path, test_dir, conf_threshold, iou_threshold, img_size)
            elif source_type == 'dir':
                results = self._process_directory(model, input_path, test_dir, conf_threshold, iou_threshold, img_size)
            elif source_type == 'webcam':
                results = self._process_webcam(model, test_dir, conf_threshold, iou_threshold, img_size)
            
            return {
                'success': True,
                'results': results,
                'output_dir': test_dir
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _process_image(self, model, image_path, output_dir, conf, iou, img_size):
        """Process a single image"""
        # Run inference
        results = model(image_path, conf=conf, iou=iou, imgsz=img_size)
        
        # Save annotated image
        output_path = os.path.join(output_dir, 'annotated_image.jpg')
        annotated_img = results[0].plot()
        cv2.imwrite(output_path, annotated_img)
        
        # Extract detection data
        detections = []
        if len(results[0].boxes) > 0:
            boxes = results[0].boxes
            for i, box in enumerate(boxes):
                detection = {
                    'bbox': box.xyxy[0].tolist(),
                    'confidence': float(box.conf[0]),
                    'class': int(box.cls[0]),
                    'class_name': results[0].names[int(box.cls[0])]
                }
                detections.append(detection)
        
        return {
            'type': 'image',
            'input_path': image_path,
            'output_path': output_path,
            'detections': detections,
            'detection_count': len(detections)
        }
    
    def _process_video(self, model, video_path, output_dir, conf, iou, img_size):
        """Process a video file"""
        cap = cv2.VideoCapture(video_path)
        
        # Get video properties
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        # Create output video writer
        output_path = os.path.join(output_dir, 'annotated_video.mp4')
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        
        frame_count = 0
        total_detections = 0
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Run inference on frame
            results = model(frame, conf=conf, iou=iou, imgsz=img_size)
            
            # Annotate frame
            annotated_frame = results[0].plot()
            out.write(annotated_frame)
            
            # Count detections
            total_detections += len(results[0].boxes) if results[0].boxes is not None else 0
            frame_count += 1
        
        cap.release()
        out.release()
        
        return {
            'type': 'video',
            'input_path': video_path,
            'output_path': output_path,
            'frame_count': frame_count,
            'total_detections': total_detections
        }
    
    def _process_directory(self, model, input_dir, output_dir, conf, iou, img_size):
        """Process all images in a directory"""
        # Create subdirectory for annotated images
        annotated_dir = os.path.join(output_dir, 'annotated_images')
        os.makedirs(annotated_dir, exist_ok=True)
        
        # Get all image files
        image_extensions = {'.jpg', '.jpeg', '.png', '.bmp'}
        image_files = []
        
        for file in os.listdir(input_dir):
            if any(file.lower().endswith(ext) for ext in image_extensions):
                image_files.append(os.path.join(input_dir, file))
        
        results = []
        total_detections = 0
        
        for image_path in image_files:
            try:
                # Run inference
                inference_results = model(image_path, conf=conf, iou=iou, imgsz=img_size)
                
                # Save annotated image
                filename = os.path.basename(image_path)
                output_path = os.path.join(annotated_dir, f'annotated_{filename}')
                annotated_img = inference_results[0].plot()
                cv2.imwrite(output_path, annotated_img)
                
                # Count detections
                detection_count = len(inference_results[0].boxes) if inference_results[0].boxes is not None else 0
                total_detections += detection_count
                
                results.append({
                    'input_path': image_path,
                    'output_path': output_path,
                    'detection_count': detection_count
                })
                
            except Exception as e:
                print(f"Error processing {image_path}: {e}")
        
        return {
            'type': 'directory',
            'input_path': input_dir,
            'output_dir': annotated_dir,
            'processed_images': len(results),
            'total_detections': total_detections,
            'results': results
        }
    
    def _process_webcam(self, model, output_dir, conf, iou, img_size):
        """Process webcam stream (placeholder - actual implementation would be handled by frontend)"""
        # This would typically be handled by the frontend sending frames via WebSocket
        # For now, return a placeholder structure
        return {
            'type': 'webcam',
            'message': 'Webcam processing should be handled by frontend WebSocket connection',
            'output_dir': output_dir
        }
    
    def process_webcam_frame(self, model_path, frame_data, conf_threshold=0.25, iou_threshold=0.45, img_size=640):
        """Process a single webcam frame"""
        try:
            # Load model
            model = YOLO(model_path)
            
            # Decode frame (assuming base64 encoded)
            import base64
            frame_bytes = base64.b64decode(frame_data)
            nparr = np.frombuffer(frame_bytes, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            # Run inference
            results = model(frame, conf=conf_threshold, iou=iou_threshold, imgsz=img_size)
            
            # Get annotated frame
            annotated_frame = results[0].plot()
            
            # Encode back to base64
            _, buffer = cv2.imencode('.jpg', annotated_frame)
            frame_base64 = base64.b64encode(buffer).decode('utf-8')
            
            # Extract detections
            detections = []
            if results[0].boxes is not None and len(results[0].boxes) > 0:
                boxes = results[0].boxes
                for box in boxes:
                    detection = {
                        'bbox': box.xyxy[0].tolist(),
                        'confidence': float(box.conf[0]),
                        'class': int(box.cls[0]),
                        'class_name': results[0].names[int(box.cls[0])]
                    }
                    detections.append(detection)
            
            return {
                'success': True,
                'annotated_frame': frame_base64,
                'detections': detections
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }