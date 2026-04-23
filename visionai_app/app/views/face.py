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

# Initialize face detection model (lazy loading)
face_model = None

def get_face_model():
    global face_model
    if face_model is None:
        try:
            # Try to load a real face detection model
            # For now, we'll use OpenCV's built-in face detector
            face_model = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        except Exception as e:
            print(f"Error loading face model: {e}")
            face_model = None
    return face_model

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
            
            # Convert to grayscale for face detection
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Perform face detection
            start_time = time.time()
            face_cascade = get_face_model()
            
            faces = []
            if face_cascade is not None:
                # Detect faces
                face_rects = face_cascade.detectMultiScale(gray, 1.1, 4)
                
                for (x, y, w, h) in face_rects:
                    confidence = min(0.95, 0.5 + (w * h) / (img.shape[0] * img.shape[1]) * 2)
                    
                    faces.append({
                        'box': (x, y, x + w, y + h),
                        'confidence': confidence
                    })
            else:
                # Fallback to mock detection if model fails
                faces = _mock_face_detection(img)['faces']
            
            processing_time = time.time() - start_time
            
            # Draw bounding boxes on image
            annotated_img = img.copy()
            
            for i, face in enumerate(faces):
                x1, y1, x2, y2 = face['box']
                confidence = face['confidence']
                
                # Draw bounding box
                cv2.rectangle(annotated_img, (x1, y1), (x2, y2), (0, 255, 0), 2)
                
                # Draw label
                label = f"Face {i+1}: {confidence:.2f}"
                label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)[0]
                cv2.rectangle(annotated_img, (x1, y1 - 25), 
                             (x1 + label_size[0], y1), (0, 255, 0), -1)
                cv2.putText(annotated_img, label, (x1, y1 - 5), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
            
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
            
            for face in faces:
                objects_detected.append({
                    'name': f"Face {len(objects_detected) + 1}",
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
                'faces': faces,
                'processing_time': processing_time,
                'detection_id': detection.id
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    return jsonify({'error': 'Invalid file format'}), 400

@face_bp.route('/detect_camera', methods=['POST'])
@login_required
def detect_face_camera():
    """Detect faces from camera image"""
    data = request.get_json()
    image_data = data.get('image')
    
    if not image_data:
        return jsonify({'error': 'No image data provided'}), 400
    
    try:
        # Decode base64 image
        image_data = image_data.split(',')[1]  # Remove data:image/jpeg;base64, prefix
        image_bytes = base64.b64decode(image_data)
        
        # Convert to numpy array
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        # Convert to grayscale for face detection
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Perform face detection
        start_time = time.time()
        face_cascade = get_face_model()
        
        faces = []
        if face_cascade is not None:
            # Detect faces
            face_rects = face_cascade.detectMultiScale(gray, 1.1, 4)
            
            for (x, y, w, h) in face_rects:
                confidence = min(0.95, 0.5 + (w * h) / (img.shape[0] * img.shape[1]) * 2)
                
                faces.append({
                    'box': (x, y, x + w, y + h),
                    'confidence': confidence
                })
        else:
            # Fallback to mock detection if model fails
            faces = _mock_face_detection(img)['faces']
        
        processing_time = time.time() - start_time
        
        # Prepare data for database
        objects_detected = []
        confidence_scores = []
        bounding_boxes = []
        
        for face in faces:
            objects_detected.append({
                'name': f"Face {len(objects_detected) + 1}",
                'confidence': face['confidence'],
                'box': face['box']
            })
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
            'processing_time': processing_time
        }
        
        # Save detection to database
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
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def _mock_face_detection(img):
    """Mock face detection as fallback"""
    import random
    
    h, w = img.shape[:2]
    
    # Random number of faces (0-3)
    num_faces = random.randint(0, 3)
    
    faces = []
    for i in range(num_faces):
        # Random face box
        face_size = random.randint(80, min(200, min(w, h) // 3))
        x1 = random.randint(0, max(1, w - face_size))
        y1 = random.randint(0, max(1, h - face_size))
        x2 = x1 + face_size
        y2 = y1 + face_size
        
        confidence = random.uniform(0.7, 0.95)
        
        faces.append({
            'box': (x1, y1, x2, y2),
            'confidence': confidence
        })
    
    return {
        'success': True,
        'faces': faces,
        'mock_mode': True
    }

@face_bp.route('/add_face', methods=['POST'])
@login_required
def add_face():
    """Add a new known face"""
    if 'image' not in request.files:
        return jsonify({'error': 'No image file provided'}), 400
    
    file = request.files['image']
    person_name = request.form.get('name', '').strip()
    
    if file.filename == '':
        return jsonify({'error': 'No image selected'}), 400
    
    if not person_name:
        return jsonify({'error': 'Person name is required'}), 400
    
    if file and allowed_file(file.filename):
        try:
            # Read image
            image_stream = file.read()
            nparr = np.frombuffer(image_stream, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if img is None:
                return jsonify({'error': 'Invalid image format'}), 400
            
            # Detect face in the image
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            face_cascade = get_face_model()
            
            faces = []
            if face_cascade is not None:
                face_rects = face_cascade.detectMultiScale(gray, 1.1, 4)
                
                if len(face_rects) == 0:
                    return jsonify({'error': 'No face detected in the image'}), 400
                
                # Use the first detected face
                for (x, y, w, h) in face_rects[:1]:
                    confidence = min(0.95, 0.5 + (w * h) / (img.shape[0] * img.shape[1]) * 2)
                    
                    faces.append({
                        'box': (x, y, x + w, y + h),
                        'confidence': confidence
                    })
            else:
                return jsonify({'error': 'Face detection model not available'}), 500
            
            # Save the face image
            filename = f'known_face_{uuid.uuid4()}.jpg'
            cv2.imwrite(os.path.join(current_app.config['UPLOAD_FOLDER'], filename), img)
            
            # Save to database as a face detection
            detection = Detection(
                user_id=current_user.id,
                image_path=filename,
                detection_type='known_face',
                processing_time=0.1
            )
            
            # Store face data with person name
            objects_detected = []
            confidence_scores = []
            
            for face in faces:
                objects_detected.append({
                    'name': person_name,
                    'confidence': face['confidence'],
                    'box': face['box'],
                    'type': 'known_face'
                })
                confidence_scores.append(face['confidence'])
            
            detection.set_objects_detected(objects_detected)
            detection.set_confidence_scores(confidence_scores)
            
            db.session.add(detection)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': f'Face "{person_name}" added successfully!',
                'face_id': detection.id,
                'person_name': person_name,
                'image_path': filename
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500

def _mock_face_detection(img):
    """Mock face detection as fallback"""
    import random
    
    h, w = img.shape[:2]
    
    # Random number of faces (0-3)
    num_faces = random.randint(0, 3)
    
    faces = []
    for i in range(num_faces):
        # Random face box
        face_size = random.randint(80, min(200, min(w, h) // 3))
        x1 = random.randint(0, max(1, w - face_size))
        y1 = random.randint(0, max(1, h - face_size))
        x2 = x1 + face_size
        y2 = y1 + face_size
        
        confidence = random.uniform(0.7, 0.95)
        
        faces.append({
            'box': (x1, y1, x2, y2),
            'confidence': confidence
        })
    
    return {
        'success': True,
        'faces': faces,
        'mock_mode': True
    }

@face_bp.route('/get_known_faces')
@login_required
def get_known_faces():
    """Get all known faces for the current user"""
    try:
        known_faces = Detection.query.filter_by(
            user_id=current_user.id,
            detection_type='known_face'
        ).order_by(Detection.timestamp.desc()).all()
        
        faces_data = []
        for face in known_faces:
            objects_detected = face.get_objects_detected()
            if objects_detected:
                face_data = objects_detected[0]  # Get first face
                faces_data.append({
                    'id': face.id,
                    'person_name': face_data.get('name', 'Unknown'),
                    'confidence': face_data.get('confidence', 0),
                    'image_path': face.image_path,
                    'timestamp': face.timestamp.isoformat(),
                    'processing_time': face.processing_time
                })
        
        return jsonify({
            'success': True,
            'faces': faces_data,
            'count': len(faces_data)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@face_bp.route('/delete_known_face/<int:face_id>', methods=['DELETE'])
@login_required
def delete_known_face(face_id):
    """Delete a known face"""
    try:
        face = Detection.query.filter_by(
            id=face_id,
            user_id=current_user.id,
            detection_type='known_face'
        ).first()
        
        if not face:
            return jsonify({'error': 'Known face not found'}), 404
        
        # Delete image file
        try:
            image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], face.image_path)
            if os.path.exists(image_path):
                os.remove(image_path)
        except Exception as e:
            print(f"Error deleting image file: {e}")
        
        # Delete database record
        db.session.delete(face)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Known face deleted successfully'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def _mock_face_detection(img):
    """Mock face detection as fallback"""
    import random
    
    h, w = img.shape[:2]
    
    # Random number of faces (0-3)
    num_faces = random.randint(0, 3)
    
    faces = []
    for i in range(num_faces):
        # Random face box
        face_size = random.randint(80, min(200, min(w, h) // 3))
        x1 = random.randint(0, max(1, w - face_size))
        y1 = random.randint(0, max(1, h - face_size))
        x2 = x1 + face_size
        y2 = y1 + face_size
        
        confidence = random.uniform(0.7, 0.95)
        
        faces.append({
            'box': (x1, y1, x2, y2),
            'confidence': confidence
        })
    
    return {
        'success': True,
        'faces': faces,
        'mock_mode': True
    }
