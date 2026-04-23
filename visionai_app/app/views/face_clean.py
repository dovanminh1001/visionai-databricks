from flask import Blueprint, render_template, request, jsonify, current_app
from flask_login import login_required, current_user
import cv2
import base64
import numpy as np
import time
import uuid
import os
from werkzeug.utils import secure_filename
from app.models.detection import Detection
from app import db

face_bp = Blueprint('face', __name__, url_prefix='/face')

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

@face_bp.route('/face_detection')
@login_required
def face_detection():
    """Face Detection interface"""
    return render_template('face/detection.html')

@face_bp.route('/detect_upload', methods=['POST'])
@login_required
def detect_face_upload():
    """Detect faces from uploaded image"""
    if 'image' not in request.files:
        return jsonify({'error': 'No image file provided'}), 400
    
    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No image selected'}), 400
    
    if file and allowed_file(file.filename):
        try:
            # Read image
            image_stream = file.read()
            nparr = np.frombuffer(image_stream, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if img is None:
                return jsonify({'error': 'Invalid image format'}), 400
            
            # Perform face detection
            start_time = time.time()
            faces = _detect_faces(img)
            processing_time = time.time() - start_time
            
            if not faces:
                return jsonify({
                    'success': True,
                    'faces': [],
                    'processing_time': processing_time,
                    'message': 'No faces detected in the image'
                })
            
            # Draw bounding boxes on image
            annotated_img = _draw_face_boxes(img, faces)
            
            # Convert annotated image to base64
            _, buffer = cv2.imencode('.jpg', annotated_img)
            annotated_image_data = base64.b64encode(buffer).decode('utf-8')
            
            # Save detection to database
            filename = f'face_{uuid.uuid4()}.jpg'
            cv2.imwrite(os.path.join(current_app.config['UPLOAD_FOLDER'], filename), img)
            
            detection = Detection(
                user_id=current_user.id,
                image_path=filename,
                detection_type='face',
                processing_time=processing_time
            )
            
            # Prepare data for database
            objects_detected = []
            confidence_scores = []
            
            for i, face in enumerate(faces):
                objects_detected.append({
                    'name': f"Face {i+1}",
                    'confidence': face['confidence'],
                    'box': face['box']
                })
                confidence_scores.append(face['confidence'])
            
            detection.set_objects_detected(objects_detected)
            detection.set_confidence_scores(confidence_scores)
            
            db.session.add(detection)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'annotated_image': f"data:image/jpeg;base64,{annotated_image_data}",
                'faces': objects_detected,
                'processing_time': processing_time,
                'detection_id': detection.id,
                'faces_count': len(faces)
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    return jsonify({'error': 'Invalid file format'}), 400

@face_bp.route('/detect_camera', methods=['POST'])
@login_required
def detect_face_camera():
    """Detect faces from camera image"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        image_data = data.get('image')
        if not image_data:
            return jsonify({'error': 'No image data provided'}), 400
        
        # Decode base64 image
        if ',' in image_data:
            image_data = image_data.split(',')[1]
        
        image_bytes = base64.b64decode(image_data)
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            return jsonify({'error': 'Invalid image format'}), 400
        
        # Perform face detection
        start_time = time.time()
        faces = _detect_faces(img)
        processing_time = time.time() - start_time
        
        # Prepare data for database and response
        objects_detected = []
        confidence_scores = []
        bounding_boxes = []
        
        for i, face in enumerate(faces):
            face_data = {
                'name': f"Face {i+1}",
                'confidence': face['confidence'],
                'box': face['box']
            }
            objects_detected.append(face_data)
            confidence_scores.append(face['confidence'])
            
            x1, y1, x2, y2 = face['box']
            bounding_boxes.append({
                'x1': x1, 'y1': y1, 'x2': x2, 'y2': y2,
                'confidence': face['confidence']
            })
        
        # Create result
        result = {
            'success': True,
            'faces': objects_detected,
            'bounding_boxes': bounding_boxes,
            'processing_time': processing_time,
            'faces_count': len(faces)
        }
        
        # Save detection to database
        try:
            filename = f'face_camera_{uuid.uuid4()}.jpg'
            cv2.imwrite(os.path.join(current_app.config['UPLOAD_FOLDER'], filename), img)
            
            detection = Detection(
                user_id=current_user.id,
                image_path=filename,
                detection_type='face',
                processing_time=processing_time
            )
            
            detection.set_objects_detected(objects_detected)
            detection.set_confidence_scores(confidence_scores)
            
            db.session.add(detection)
            db.session.commit()
        except Exception as db_error:
            print(f"Database error (non-critical): {db_error}")
        
        return jsonify(result)
        
    except Exception as e:
        print(f"Camera detection error: {e}")
        return jsonify({'error': str(e)}), 500

@face_bp.route('/delete_detection/<int:detection_id>', methods=['DELETE'])
@login_required
def delete_detection(detection_id):
    """Delete a face detection"""
    try:
        detection = Detection.query.filter_by(
            id=detection_id,
            user_id=current_user.id,
            detection_type='face'
        ).first()
        
        if not detection:
            return jsonify({'error': 'Detection not found'}), 404
        
        # Delete image file
        try:
            image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], detection.image_path)
            if os.path.exists(image_path):
                os.remove(image_path)
        except Exception as e:
            print(f"Error deleting image file: {e}")
        
        # Delete database record
        db.session.delete(detection)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Detection deleted successfully'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@face_bp.route('/delete_all', methods=['DELETE'])
@login_required
def delete_all_detections():
    """Delete all face detections for current user"""
    try:
        detections = Detection.query.filter_by(
            user_id=current_user.id,
            detection_type='face'
        ).all()
        
        # Delete all image files
        for detection in detections:
            try:
                image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], detection.image_path)
                if os.path.exists(image_path):
                    os.remove(image_path)
            except Exception as e:
                print(f"Error deleting image file {detection.image_path}: {e}")
        
        # Delete all database records
        for detection in detections:
            db.session.delete(detection)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'All {len(detections)} face detections deleted successfully'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def _detect_faces(img):
    """Detect faces in image using OpenCV Haar Cascade"""
    try:
        # Load face cascade
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        
        if face_cascade.empty():
            print("Error loading face cascade classifier")
            return []
        
        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Detect faces
        faces = face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30),
            flags=cv2.CASCADE_SCALE_IMAGE
        )
        
        # Convert to our format
        face_list = []
        for (x, y, w, h) in faces:
            # Calculate confidence based on face size and position
            confidence = min(0.95, 0.5 + (w * h) / (img.shape[0] * img.shape[1]) * 3)
            
            face_list.append({
                'box': (x, y, x + w, y + h),
                'confidence': confidence
            })
        
        return face_list
        
    except Exception as e:
        print(f"Face detection error: {e}")
        return []

def _draw_face_boxes(img, faces):
    """Draw bounding boxes and labels on image"""
    annotated_img = img.copy()
    
    for i, face in enumerate(faces):
        x1, y1, x2, y2 = face['box']
        confidence = face['confidence']
        
        # Choose color based on confidence
        if confidence > 0.8:
            color = (0, 255, 0)  # Green
        elif confidence > 0.6:
            color = (0, 255, 255)  # Yellow
        else:
            color = (0, 0, 255)  # Red
        
        # Draw bounding box
        cv2.rectangle(annotated_img, (x1, y1), (x2, y2), color, 2)
        
        # Draw label
        label = f"Face {i+1}: {confidence:.2f}"
        label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)[0]
        
        # Draw label background
        cv2.rectangle(annotated_img, (x1, y1 - 25), 
                     (x1 + label_size[0] + 10, y1), color, -1)
        
        # Draw label text
        cv2.putText(annotated_img, label, (x1 + 5, y1 - 5), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
    
    return annotated_img
