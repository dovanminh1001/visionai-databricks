"""
db_service.py — Centralized service for saving detection results to Databricks Catalog.

Tất cả các chức năng nhận diện trên web app đều gọi qua service này
để đảm bảo dữ liệu được lưu nhất quán, có error handling và logging đầy đủ.
Dữ liệu được đẩy thẳng lên Databricks Unity Catalog qua databricks-sqlalchemy.
"""

import os
import uuid
import logging
from datetime import datetime
from flask import current_app
from flask_login import current_user

from app import db
from app.models.detection import Detection

# Configure logging
logger = logging.getLogger(__name__)


def save_detection(
    detection_type: str,
    objects_detected: list,
    confidence_scores: list,
    image: None,          # numpy image array (BGR)
    image_prefix: str = None,
    processing_time: float = 0.0,
    user_id: int = None
) -> Detection | None:
    """
    Lưu kết quả nhận diện vào bảng detections trên Databricks Catalog.

    Args:
        detection_type: Loại nhận diện ('camera', 'upload', 'face_upload',
                        'face_camera', 'emotion', 'color', 'classification')
        objects_detected: Danh sách object/kết quả nhận diện (list of dicts)
        confidence_scores: Danh sách điểm tin cậy tương ứng (list of floats)
        image: numpy array ảnh (BGR) để lưu thành file .jpg
        image_prefix: Tiền tố tên file (mặc định = detection_type)
        processing_time: Thời gian xử lý tính bằng giây
        user_id: ID user (mặc định lấy từ current_user)

    Returns:
        Detection object nếu thành công, None nếu thất bại
    """
    try:
        # Xác định user_id
        if user_id is None:
            try:
                user_id = current_user.id if current_user.is_authenticated else 1
            except Exception:
                user_id = 1

        # Lưu ảnh vào thư mục uploads
        filename = _save_image(image, image_prefix or detection_type)

        # Tạo bản ghi Detection
        detection = Detection(
            user_id=user_id,
            image_path=filename,
            detection_type=detection_type,
            processing_time=processing_time
        )
        detection.set_objects_detected(objects_detected)
        detection.set_confidence_scores(confidence_scores)

        # Ghi vào Databricks Catalog
        db.session.add(detection)
        db.session.commit()

        # Trigger background pipeline update to update Databricks Gold tables in real-time
        try:
            from threading import Thread
            Thread(target=trigger_pipeline_update).start()
        except Exception as te:
            logger.warning("[DB] Failed to trigger background pipeline update: %s", str(te))

        logger.info(
            "[DB] Saved detection | type=%s | user=%s | objects=%d | id=%s",
            detection_type, user_id, len(objects_detected), detection.id
        )
        return detection

    except Exception as e:
        # Rollback để tránh session bị treo
        try:
            db.session.rollback()
        except Exception:
            pass
        logger.error(
            "[DB] Failed to save detection | type=%s | error=%s",
            detection_type, str(e),
            exc_info=True
        )
        return None


def trigger_pipeline_update():
    """
    Chạy các câu lệnh SQL Silver và Gold trực tiếp trên Databricks thông qua background thread
    để cập nhật biểu đồ trên Databricks Dashboard gần như thời gian thực (Real-time).
    """
    import os
    import logging
    from urllib.parse import urlparse, parse_qs
    from databricks import sql as databricks_sql
    
    logger = logging.getLogger(__name__)
    
    database_url = os.environ.get('DATABASE_URL')
    if not database_url or 'databricks' not in database_url:
        logger.warning("[DB-Pipeline] DATABASE_URL is not set or not Databricks. Skipping sync.")
        return
        
    try:
        parsed = urlparse(database_url)
        host = parsed.hostname
        token = parsed.password
        params = parse_qs(parsed.query)
        http_path = params.get('http_path', [''])[0]
        catalog = params.get('catalog', ['visionai_catalog'])[0]
        schema = params.get('schema', ['default'])[0]
        
        logger.info("[DB-Pipeline] Starting background sync for Silver and Gold tables...")
        
        connection = databricks_sql.connect(
            server_hostname=host,
            http_path=http_path,
            access_token=token,
            catalog=catalog,
            schema=schema
        )
        cursor = connection.cursor()
        
        # 1. Cập nhật tầng Silver
        cursor.execute(f"""
            CREATE OR REPLACE TABLE {catalog}.silver.detections_enriched AS
            SELECT
                detection_id,
                user_id,
                username,
                image_path,
                detection_type,
                objects_json,
                capture_time,
                processing_time,
                HOUR(capture_time) AS hour_of_day,
                CASE
                    WHEN HOUR(capture_time) BETWEEN 6 AND 11  THEN 'MORNING'
                    WHEN HOUR(capture_time) BETWEEN 12 AND 17 THEN 'AFTERNOON'
                    WHEN HOUR(capture_time) BETWEEN 18 AND 22 THEN 'EVENING'
                    ELSE 'NIGHT'
                END AS time_shift,
                CASE
                    WHEN detection_type = 'upload'         THEN 'Object Detection'
                    WHEN detection_type = 'camera'         THEN 'Realtime Detection'
                    WHEN detection_type = 'face_upload'    THEN 'Face Recognition'
                    WHEN detection_type = 'color'          THEN 'Color Analysis'
                    WHEN detection_type = 'classification' THEN 'Classification'
                    ELSE 'Other'
                END AS ai_feature,
                CASE
                    WHEN processing_time < 0.1  THEN 'FAST'
                    WHEN processing_time < 0.5  THEN 'NORMAL'
                    WHEN processing_time < 1.0  THEN 'SLOW'
                    ELSE 'VERY_SLOW'
                END AS speed_grade,
                DAYOFWEEK(capture_time) AS day_of_week,
                DATEDIFF(current_date(), DATE(capture_time)) AS days_ago,
                current_timestamp() AS processed_at
            FROM {catalog}.bronze.raw_detections
        """)
        
        # 2. Cập nhật Gold 1: Thống kê theo Chức năng AI
        cursor.execute(f"""
            CREATE OR REPLACE TABLE {catalog}.gold.detection_by_feature AS
            SELECT
                ai_feature,
                detection_type,
                COUNT(*)                        AS total_detections,
                ROUND(AVG(processing_time), 3)  AS avg_processing_sec,
                COUNT(DISTINCT username)        AS unique_users
            FROM {catalog}.silver.detections_enriched
            GROUP BY ai_feature, detection_type
            ORDER BY total_detections DESC
        """)
        
        # 3. Cập nhật Gold 2: Thống kê theo Ca làm việc
        cursor.execute(f"""
            CREATE OR REPLACE TABLE {catalog}.gold.detection_by_shift AS
            SELECT
                time_shift,
                COUNT(*)                        AS total_detections,
                COUNT(DISTINCT username)        AS active_users,
                ROUND(AVG(processing_time), 3)  AS avg_processing_sec
            FROM {catalog}.silver.detections_enriched
            GROUP BY time_shift
            ORDER BY
                CASE time_shift
                    WHEN 'MORNING'   THEN 1
                    WHEN 'AFTERNOON' THEN 2
                    WHEN 'EVENING'   THEN 3
                    WHEN 'NIGHT'     THEN 4
                END
        """)
        
        # 4. Cập nhật Gold 3: Hoạt động theo Giờ
        cursor.execute(f"""
            CREATE OR REPLACE TABLE {catalog}.gold.hourly_activity AS
            SELECT
                hour_of_day,
                COUNT(*)                   AS total_detections,
                COUNT(DISTINCT username)   AS active_users
            FROM {catalog}.silver.detections_enriched
            GROUP BY hour_of_day
            ORDER BY hour_of_day
        """)
        
        # 5. Cập nhật Gold 4: Hiệu suất tốc độ xử lý
        cursor.execute(f"""
            CREATE OR REPLACE TABLE {catalog}.gold.speed_analysis AS
            SELECT
                speed_grade,
                ai_feature,
                COUNT(*)                        AS total_detections,
                ROUND(AVG(processing_time), 3)  AS avg_time_sec,
                ROUND(MIN(processing_time), 3)  AS fastest_sec,
                ROUND(MAX(processing_time), 3)  AS slowest_sec
            FROM {catalog}.silver.detections_enriched
            GROUP BY speed_grade, ai_feature
            ORDER BY avg_time_sec
        """)
        
        connection.commit()
        cursor.close()
        connection.close()
        logger.info("[DB-Pipeline] Background sync for Silver and Gold tables completed successfully!")
    except Exception as e:
        logger.error("[DB-Pipeline] Failed background sync: %s", str(e), exc_info=True)


def _save_image(image, prefix: str) -> str:
    """
    Lưu numpy image array ra file .jpg trong thư mục UPLOAD_FOLDER.
    Trả về tên file đã lưu.
    """
    import cv2

    filename = f"{prefix}_{uuid.uuid4()}.jpg"
    filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)

    if image is not None:
        cv2.imwrite(filepath, image)
    else:
        # Tạo file placeholder nếu không có ảnh
        logger.warning("[DB] No image provided for detection type '%s', saving placeholder.", prefix)

    return filename


def save_annotated_image(image, original_filename: str) -> str:
    """
    Lưu ảnh annotated (đã vẽ bounding box) bên cạnh ảnh gốc.
    Trả về tên file annotated.
    """
    import cv2

    annotated_filename = f"annotated_{original_filename}"
    annotated_filepath = os.path.join(
        current_app.config['UPLOAD_FOLDER'], annotated_filename
    )
    if image is not None:
        cv2.imwrite(annotated_filepath, image)
    return annotated_filename


def get_recent_detections(detection_type: str = None, limit: int = 12) -> list:
    """
    Lấy danh sách detection gần nhất của current_user từ Databricks Catalog.

    Args:
        detection_type: Lọc theo loại (None = tất cả)
        limit: Số bản ghi tối đa

    Returns:
        List of Detection objects
    """
    try:
        try:
            user_id = current_user.id if current_user.is_authenticated else 1
        except Exception:
            user_id = 1

        query = Detection.query.filter_by(user_id=user_id)
        if detection_type:
            query = query.filter_by(detection_type=detection_type)

        return query.order_by(Detection.timestamp.desc()).limit(limit).all()

    except Exception as e:
        logger.error("[DB] Failed to fetch detections | error=%s", str(e))
        return []


def delete_detection_by_id(detection_id: int, user_id: int = None) -> bool:
    """
    Xóa một detection theo ID khỏi Databricks Catalog và xóa file ảnh liên quan.

    Returns:
        True nếu xóa thành công, False nếu thất bại
    """
    try:
        if user_id is None:
            try:
                user_id = current_user.id
            except Exception:
                return False

        detection = Detection.query.filter_by(
            id=detection_id, user_id=user_id
        ).first()

        if not detection:
            logger.warning("[DB] Detection %d not found for user %d", detection_id, user_id)
            return False

        # Xóa file ảnh
        _delete_image_file(detection.image_path)

        db.session.delete(detection)
        db.session.commit()

        # Trigger background pipeline update to update Databricks Gold tables
        try:
            from threading import Thread
            Thread(target=trigger_pipeline_update).start()
        except Exception as te:
            logger.warning("[DB] Failed to trigger background pipeline update: %s", str(te))

        logger.info("[DB] Deleted detection %d for user %d", detection_id, user_id)
        return True

    except Exception as e:
        try:
            db.session.rollback()
        except Exception:
            pass
        logger.error("[DB] Failed to delete detection %d | error=%s", detection_id, str(e))
        return False


def _delete_image_file(image_path: str):
    """Xóa file ảnh trong thư mục uploads nếu tồn tại."""
    try:
        if image_path:
            full_path = os.path.join(current_app.config['UPLOAD_FOLDER'], image_path)
            if os.path.exists(full_path):
                os.remove(full_path)
    except Exception as e:
        logger.warning("[DB] Could not delete image file '%s': %s", image_path, str(e))
