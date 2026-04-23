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
from functools import lru_cache

emotion_bp = Blueprint('emotion', __name__, url_prefix='/emotion')

# Cache for recent emotion results to reduce processing
emotion_cache = {}
cache_timeout = 5  # seconds

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

@lru_cache(maxsize=32)
def get_cached_emotion_result(image_hash):
    """Get cached emotion result to reduce processing"""
    current_time = time.time()
    if image_hash in emotion_cache:
        cached_result, cached_time = emotion_cache[image_hash]
        if current_time - cached_time < cache_timeout:
            return cached_result
    return None

def cache_emotion_result(image_hash, result):
    """Cache emotion result"""
    emotion_cache[image_hash] = (result, time.time())
    
    # Clean old cache entries
    current_time = time.time()
    keys_to_remove = []
    for key in emotion_cache:
        cached_result, cached_time = emotion_cache[key]
        if current_time - cached_time > cache_timeout * 2:
            keys_to_remove.append(key)
    
    for key in keys_to_remove:
        del emotion_cache[key]

@emotion_bp.route('/emotion_detection')
@login_required
def emotion_detection():
    """Emotion Detection interface"""
    return render_template('emotion/emotion_detection.html')

@emotion_bp.route('/detect_upload', methods=['POST'])
@login_required
def detect_emotion_upload():
    """Detect emotions from uploaded image"""
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
            
            # Mock emotion detection
            start_time = time.time()
            emotion_results = _mock_emotion_detection(img)
            processing_time = time.time() - start_time
            
            if not emotion_results['success']:
                return jsonify({'error': emotion_results['error']}), 500
            
            # Draw bounding box on image
            annotated_img = img.copy()
            h, w = img.shape[:2]
            face_box = (w//4, h//4, 3*w//4, 3*h//4)
            
            # Get dominant emotion for color coding
            dominant_emotion = emotion_results['dominant_emotion']
            emotion_colors = {
                'Vui vẻ': (0, 255, 0),
                'Buồn bã': (255, 0, 0),
                'Giận dữ': (0, 0, 255),
                'Sợ hãi': (128, 0, 128),
                'Ngạc nhiên': (0, 255, 255),
                'Chán ghét': (255, 255, 0),
                'Bình thường': (128, 128, 128)
            }
            
            color = emotion_colors.get(dominant_emotion, (0, 255, 0))
            
            # Draw bounding box for dominant emotion
            cv2.rectangle(annotated_img, (face_box[0], face_box[1]), (face_box[2], face_box[3]), color, 2)
            
            # Draw label
            label = f"{dominant_emotion} {(emotion_results['confidence'] * 100):.1f}%"
            label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)[0]
            cv2.rectangle(annotated_img, (face_box[0], face_box[1] - 25), 
                         (face_box[0] + label_size[0], face_box[1]), color, -1)
            cv2.putText(annotated_img, label, (face_box[0], face_box[1] - 5), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
            
            # Convert annotated image to base64
            _, buffer = cv2.imencode('.jpg', annotated_img)
            annotated_image_data = base64.b64encode(buffer).decode('utf-8')
            
            # Save detection to database
            filename = f'emotion_{uuid.uuid4()}.jpg'
            cv2.imwrite(os.path.join(current_app.config['UPLOAD_FOLDER'], filename), img)
            
            detection = Detection(
                user_id=current_user.id,
                image_path=filename,
                detection_type='emotion',
                processing_time=processing_time
            )
            
            # Prepare data for database
            objects_detected = []
            confidence_scores = []
            
            # Only create bounding box for dominant emotion
            objects_detected.append({
                'name': dominant_emotion,
                'confidence': emotion_results['confidence'],
                'box': face_box
            })
            confidence_scores.append(emotion_results['confidence'])
            
            detection.set_objects_detected(objects_detected)
            detection.set_confidence_scores(confidence_scores)
            
            db.session.add(detection)
            db.session.commit()
            
            # Convert emotions to expected format
            emotions_list = []
            for emotion_name, emotion_confidence in emotion_results['emotions'].items():
                emotions_list.append({
                    'name': emotion_name,
                    'confidence': emotion_confidence
                })
            
            return jsonify({
                'success': True,
                'annotated_image': f"data:image/jpeg;base64,{annotated_image_data}",
                'dominant_emotion': emotion_results['dominant_emotion'],
                'confidence': emotion_results['confidence'],
                'emotions': emotions_list,
                'processing_time': processing_time,
                'detection_id': detection.id
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    return jsonify({'error': 'Invalid file format'}), 400

@emotion_bp.route('/detect_camera', methods=['POST'])
@login_required
def detect_emotion_camera():
    """Detect emotions from camera image"""
    data = request.get_json()
    image_data = data.get('image')
    
    if not image_data:
        return jsonify({'error': 'No image data provided'}), 400
    
    try:
        # Create hash for caching
        import hashlib
        image_hash = hashlib.md5(image_data.encode()).hexdigest()[:16]
        
        # Check cache first
        cached_result = get_cached_emotion_result(image_hash)
        if cached_result:
            return jsonify(cached_result)
        
        # Decode base64 image
        image_data = image_data.split(',')[1]  # Remove data:image/jpeg;base64, prefix
        image_bytes = base64.b64decode(image_data)
        
        # Convert to numpy array
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        # Perform emotion detection
        start_time = time.time()
        emotion_results = _mock_emotion_detection(img)
        processing_time = time.time() - start_time
        
        if not emotion_results['success']:
            return jsonify({'error': emotion_results['error']}), 500
        
        # Prepare data for database
        objects_detected = []
        confidence_scores = []
        bounding_boxes = []
        
        # Mock face box for emotion display with emotion-based colors
        h, w = img.shape[:2]
        face_box = (w//4, h//4, 3*w//4, 3*h//4)
        
        # Get dominant emotion for color coding
        dominant_emotion = emotion_results['dominant_emotion']
        dominant_confidence = emotion_results['confidence']
        
        emotion_colors = {
            'Vui vẻ': (0, 255, 0),
            'Buồn bã': (255, 0, 0),
            'Giận dữ': (0, 0, 255),
            'Sợ hãi': (128, 0, 128),
            'Ngạc nhiên': (0, 255, 255),
            'Chán ghét': (255, 255, 0),
            'Bình thường': (128, 128, 128)
        }
        
        color = emotion_colors.get(dominant_emotion, (0, 255, 0))
        
        # Only create bounding box for dominant emotion
        objects_detected.append({
            'name': dominant_emotion,
            'confidence': dominant_confidence,
            'box': face_box
        })
        confidence_scores.append(dominant_confidence)
        bounding_boxes.append({
            'x1': face_box[0],
            'y1': face_box[1],
            'x2': face_box[2],
            'y2': face_box[3],
            'emotion': dominant_emotion,
            'confidence': dominant_confidence,
            'color': color
        })
        
        # Create result
        result = {
            'success': True,
            'emotions': objects_detected,
            'dominant_emotion': emotion_results['dominant_emotion'],
            'confidence': emotion_results['confidence'],
            'processing_time': processing_time,
            'bounding_boxes': bounding_boxes,
            'cached': False
        }
        
        # Cache the result
        cache_emotion_result(image_hash, result)
        
        # Save detection to database (only for new detections, not cached)
        if not cached_result:
            filename = f'emotion_camera_{uuid.uuid4()}.jpg'
            cv2.imwrite(os.path.join(current_app.config['UPLOAD_FOLDER'], filename), img)
            
            detection = Detection(
                user_id=current_user.id,
                image_path=filename,
                detection_type='emotion',
                processing_time=processing_time
            )
            
            detection.set_objects_detected(objects_detected)
            detection.set_confidence_scores(confidence_scores)
            
            db.session.add(detection)
            db.session.commit()
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@emotion_bp.route('/api/recent-detections')
@login_required
def get_recent_detections():
    """Get recent emotion detections for display"""
    try:
        # Get recent emotion detections from database
        detections = Detection.query.filter_by(
            detection_type='emotion',
            user_id=current_user.id
        ).order_by(Detection.timestamp.desc()).limit(10).all()
        
        recent_detections = []
        for detection in detections:
            objects_detected = detection.get_objects_detected()
            if objects_detected:
                # Get dominant emotion
                dominant_emotion = max(objects_detected, key=lambda x: x.get('confidence', 0))
                
                recent_detections.append({
                    'id': detection.id,
                    'timestamp': detection.timestamp.isoformat(),
                    'dominant_emotion': dominant_emotion.get('name', 'Unknown'),
                    'confidence': dominant_emotion.get('confidence', 0),
                    'processing_time': detection.processing_time,
                    'image_path': detection.image_path
                })
        
        return jsonify({
            'success': True,
            'detections': recent_detections,
            'count': len(recent_detections)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@emotion_bp.route('/uploads/<filename>')
@login_required
def uploaded_file(filename):
    """Serve uploaded files"""
    try:
        from flask import send_from_directory
        return send_from_directory(
            current_app.config['UPLOAD_FOLDER'], 
            filename, 
            as_attachment=False
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 404

def _mock_emotion_detection(img):
    """Mock emotion detection"""
    import random
    import time
    import hashlib
    
    # Create image hash for consistent results
    image_hash = hashlib.md5(str(img.shape).encode()).hexdigest()[:8]
    
    # Emotion patterns
    emotion_patterns = [
        {'Vui vẻ': 0.85, 'Buồn bã': 0.05, 'Giận dữ': 0.02, 'Sợ hãi': 0.01, 'Ngạc nhiên': 0.05, 'Chán ghét': 0.01, 'Bình thường': 0.01},
        {'Vui vẻ': 0.75, 'Buồn bã': 0.10, 'Giận dữ': 0.03, 'Sợ hãi': 0.02, 'Ngạc nhiên': 0.08, 'Chán ghét': 0.01, 'Bình thường': 0.01},
        {'Buồn bã': 0.65, 'Vui vẻ': 0.15, 'Giận dữ': 0.08, 'Sợ hãi': 0.05, 'Ngạc nhiên': 0.02, 'Chán ghét': 0.03, 'Bình thường': 0.02},
        {'Giận dữ': 0.60, 'Buồn bã': 0.15, 'Vui vẻ': 0.08, 'Sợ hãi': 0.10, 'Ngạc nhiên': 0.05, 'Chán ghét': 0.02, 'Bình thường': 0.02},
        {'Ngạc nhiên': 0.70, 'Vui vẻ': 0.10, 'Buồn bã': 0.05, 'Giận dữ': 0.03, 'Sợ hãi': 0.08, 'Chán ghét': 0.02, 'Bình thường': 0.02},
        {'Bình thường': 0.55, 'Vui vẻ': 0.20, 'Buồn bã': 0.10, 'Giận dữ': 0.05, 'Sợ hãi': 0.03, 'Ngạc nhiên': 0.05, 'Chán ghét': 0.02}
    ]
    
    # Use hash to select pattern for consistency
    pattern_index = int(image_hash, 16) % len(emotion_patterns)
    selected_pattern = emotion_patterns[pattern_index]
    
    # Add small variation
    emotions = {}
    for emotion, base_confidence in selected_pattern.items():
        variation = random.uniform(-0.05, 0.05)
        final_confidence = max(0.01, min(0.95, base_confidence + variation))
        emotions[emotion] = round(final_confidence, 3)
    
    # Get dominant emotion
    dominant_emotion = max(emotions.items(), key=lambda x: x[1])
    
    return {
        'success': True,
        'emotions': emotions,
        'dominant_emotion': dominant_emotion[0],
        'confidence': dominant_emotion[1],
        'mock_mode': True,
        'timestamp': time.time()
    }
