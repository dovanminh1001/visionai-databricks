-- data/06_seed_detection_statistics.sql
-- Script khởi tạo thêm dữ liệu detection phong phú cho admin
-- Giúp Dashboard hiển thị biểu đồ thống kê với dữ liệu đa dạng và trải đều theo thời gian

USE VisionAIDB;
GO

DECLARE @admin_id INT;
SELECT @admin_id = id FROM users WHERE username = 'admin';

IF @admin_id IS NULL
BEGIN
    PRINT N'[ERROR] Admin user not found. Run 04_seed_users.sql first!';
    RETURN;
END

-- =============================================
-- THÊM DETECTION ĐA DẠNG THEO THỜI GIAN CHO ADMIN
-- Giúp Dashboard có đủ dữ liệu để hiển thị top objects,
-- thống kê camera vs upload, và lịch sử hoạt động
-- =============================================

-- Ngày -27: Upload ảnh phòng học
IF NOT EXISTS (SELECT 1 FROM detections WHERE image_path = 'seed_stats_classroom.jpg')
BEGIN
    INSERT INTO detections (user_id, image_path, detection_type, objects_detected, confidence_scores, timestamp, processing_time)
    VALUES (
        @admin_id,
        'seed_stats_classroom.jpg',
        'upload',
        '[{"name": {"en": "person", "vi": "Người"}, "confidence": 0.91, "x1": 50, "y1": 60, "x2": 200, "y2": 400, "class": "person"}, {"name": {"en": "person", "vi": "Người"}, "confidence": 0.88, "x1": 220, "y1": 70, "x2": 360, "y2": 410, "class": "person"}, {"name": {"en": "laptop", "vi": "Máy tính xách tay"}, "confidence": 0.85, "x1": 80, "y1": 250, "x2": 180, "y2": 350, "class": "laptop"}, {"name": {"en": "chair", "vi": "Cái ghế"}, "confidence": 0.76, "x1": 30, "y1": 300, "x2": 200, "y2": 470, "class": "chair"}, {"name": {"en": "book", "vi": "Sách"}, "confidence": 0.71, "x1": 150, "y1": 280, "x2": 210, "y2": 320, "class": "book"}]',
        '[0.91, 0.88, 0.85, 0.76, 0.71]',
        DATEADD(DAY, -27, GETUTCDATE()),
        0.189
    );
    PRINT N'[OK] Stats: classroom scene (5 objects)';
END

-- Ngày -24: Camera đường phố
IF NOT EXISTS (SELECT 1 FROM detections WHERE image_path = 'seed_stats_street.jpg')
BEGIN
    INSERT INTO detections (user_id, image_path, detection_type, objects_detected, confidence_scores, timestamp, processing_time)
    VALUES (
        @admin_id,
        'seed_stats_street.jpg',
        'camera',
        '[{"en": "car", "vi": "Ô tô"}, {"en": "car", "vi": "Ô tô"}, {"en": "motorcycle", "vi": "Xe máy"}, {"en": "person", "vi": "Người"}, {"en": "traffic light", "vi": "Đèn giao thông"}]',
        '[0.93, 0.89, 0.86, 0.82, 0.77]',
        DATEADD(DAY, -24, GETUTCDATE()),
        0.125
    );
    PRINT N'[OK] Stats: street scene (5 objects)';
END

-- Ngày -21: Upload ảnh bếp
IF NOT EXISTS (SELECT 1 FROM detections WHERE image_path = 'seed_stats_kitchen.jpg')
BEGIN
    INSERT INTO detections (user_id, image_path, detection_type, objects_detected, confidence_scores, timestamp, processing_time)
    VALUES (
        @admin_id,
        'seed_stats_kitchen.jpg',
        'upload',
        '[{"name": {"en": "bottle", "vi": "Chai"}, "confidence": 0.90, "x1": 100, "y1": 50, "x2": 160, "y2": 300, "class": "bottle"}, {"name": {"en": "cup", "vi": "Cốc"}, "confidence": 0.87, "x1": 200, "y1": 80, "x2": 260, "y2": 200, "class": "cup"}, {"name": {"en": "bowl", "vi": "Tô"}, "confidence": 0.83, "x1": 300, "y1": 100, "x2": 420, "y2": 200, "class": "bowl"}, {"name": {"en": "refrigerator", "vi": "Tủ lạnh"}, "confidence": 0.78, "x1": 450, "y1": 0, "x2": 640, "y2": 480, "class": "refrigerator"}]',
        '[0.90, 0.87, 0.83, 0.78]',
        DATEADD(DAY, -21, GETUTCDATE()),
        0.156
    );
    PRINT N'[OK] Stats: kitchen scene (4 objects)';
END

-- Ngày -19: Camera công viên
IF NOT EXISTS (SELECT 1 FROM detections WHERE image_path = 'seed_stats_park.jpg')
BEGIN
    INSERT INTO detections (user_id, image_path, detection_type, objects_detected, confidence_scores, timestamp, processing_time)
    VALUES (
        @admin_id,
        'seed_stats_park.jpg',
        'camera',
        '[{"en": "dog", "vi": "Chó"}, {"en": "person", "vi": "Người"}, {"en": "bench", "vi": "Ghế dài"}, {"en": "potted plant", "vi": "Cây cảnh"}]',
        '[0.92, 0.88, 0.75, 0.70]',
        DATEADD(DAY, -19, GETUTCDATE()),
        0.108
    );
    PRINT N'[OK] Stats: park scene (4 objects)';
END

-- Ngày -16: Upload ảnh phòng khách
IF NOT EXISTS (SELECT 1 FROM detections WHERE image_path = 'seed_stats_livingroom.jpg')
BEGIN
    INSERT INTO detections (user_id, image_path, detection_type, objects_detected, confidence_scores, timestamp, processing_time)
    VALUES (
        @admin_id,
        'seed_stats_livingroom.jpg',
        'upload',
        '[{"name": {"en": "tv", "vi": "Tivi"}, "confidence": 0.94, "x1": 100, "y1": 50, "x2": 500, "y2": 300, "class": "tv"}, {"name": {"en": "couch", "vi": "Sô pha"}, "confidence": 0.89, "x1": 20, "y1": 280, "x2": 620, "y2": 470, "class": "couch"}, {"name": {"en": "remote", "vi": "Điều khiển"}, "confidence": 0.72, "x1": 300, "y1": 350, "x2": 350, "y2": 390, "class": "remote"}, {"name": {"en": "vase", "vi": "Bình hoa"}, "confidence": 0.68, "x1": 550, "y1": 100, "x2": 610, "y2": 260, "class": "vase"}]',
        '[0.94, 0.89, 0.72, 0.68]',
        DATEADD(DAY, -16, GETUTCDATE()),
        0.142
    );
    PRINT N'[OK] Stats: living room scene (4 objects)';
END

-- Ngày -13: Camera siêu thị
IF NOT EXISTS (SELECT 1 FROM detections WHERE image_path = 'seed_stats_market.jpg')
BEGIN
    INSERT INTO detections (user_id, image_path, detection_type, objects_detected, confidence_scores, timestamp, processing_time)
    VALUES (
        @admin_id,
        'seed_stats_market.jpg',
        'camera',
        '[{"en": "person", "vi": "Người"}, {"en": "person", "vi": "Người"}, {"en": "person", "vi": "Người"}, {"en": "handbag", "vi": "Túi xách"}, {"en": "bottle", "vi": "Chai"}, {"en": "backpack", "vi": "Balo"}]',
        '[0.95, 0.92, 0.87, 0.81, 0.76, 0.73]',
        DATEADD(DAY, -13, GETUTCDATE()),
        0.178
    );
    PRINT N'[OK] Stats: market scene (6 objects)';
END

-- Ngày -9: Upload ảnh giao thông
IF NOT EXISTS (SELECT 1 FROM detections WHERE image_path = 'seed_stats_traffic.jpg')
BEGIN
    INSERT INTO detections (user_id, image_path, detection_type, objects_detected, confidence_scores, timestamp, processing_time)
    VALUES (
        @admin_id,
        'seed_stats_traffic.jpg',
        'upload',
        '[{"name": {"en": "truck", "vi": "Xe tải"}, "confidence": 0.91, "x1": 200, "y1": 150, "x2": 550, "y2": 420, "class": "truck"}, {"name": {"en": "car", "vi": "Ô tô"}, "confidence": 0.88, "x1": 50, "y1": 200, "x2": 180, "y2": 350, "class": "car"}, {"name": {"en": "traffic light", "vi": "Đèn giao thông"}, "confidence": 0.84, "x1": 580, "y1": 20, "x2": 630, "y2": 120, "class": "traffic light"}, {"name": {"en": "stop sign", "vi": "Biển báo dừng"}, "confidence": 0.79, "x1": 10, "y1": 30, "x2": 60, "y2": 100, "class": "stop sign"}]',
        '[0.91, 0.88, 0.84, 0.79]',
        DATEADD(DAY, -9, GETUTCDATE()),
        0.163
    );
    PRINT N'[OK] Stats: traffic scene (4 objects)';
END

-- Ngày -6: Color Detection phong cảnh thiên nhiên
IF NOT EXISTS (SELECT 1 FROM detections WHERE image_path = 'seed_stats_nature_color.jpg')
BEGIN
    INSERT INTO detections (user_id, image_path, detection_type, objects_detected, confidence_scores, timestamp, processing_time)
    VALUES (
        @admin_id,
        'seed_stats_nature_color.jpg',
        'color',
        '[{"rgb": [39, 174, 96], "hex": "#27ae60", "name": "Green", "percentage": 45.20}, {"rgb": [52, 152, 219], "hex": "#3498db", "name": "Blue", "percentage": 28.50}, {"rgb": [236, 240, 241], "hex": "#ecf0f1", "name": "White", "percentage": 14.10}, {"rgb": [127, 140, 141], "hex": "#7f8c8d", "name": "Gray", "percentage": 8.30}, {"rgb": [139, 69, 19], "hex": "#8b4513", "name": "Brown", "percentage": 3.90}]',
        '[45.20, 28.50, 14.10, 8.30, 3.90]',
        DATEADD(DAY, -6, GETUTCDATE()),
        0.029
    );
    PRINT N'[OK] Stats: nature color detection';
END

-- Ngày -4: Face Detection nhiều khuôn mặt
IF NOT EXISTS (SELECT 1 FROM detections WHERE image_path = 'seed_stats_group_face.jpg')
BEGIN
    INSERT INTO detections (user_id, image_path, detection_type, objects_detected, confidence_scores, timestamp, processing_time)
    VALUES (
        @admin_id,
        'seed_stats_group_face.jpg',
        'face_upload',
        '[{"box": [50, 60, 150, 170], "confidence": 0.96, "name": "Unknown"}, {"box": [220, 50, 140, 160], "confidence": 0.93, "name": "Unknown"}, {"box": [400, 70, 160, 180], "confidence": 0.91, "name": "Unknown"}, {"box": [100, 280, 130, 150], "confidence": 0.87, "name": "Unknown"}]',
        '[0.96, 0.93, 0.91, 0.87]',
        DATEADD(DAY, -4, GETUTCDATE()),
        0.095
    );
    PRINT N'[OK] Stats: group face detection (4 faces)';
END

-- Ngày -2: Emotion giận dữ
IF NOT EXISTS (SELECT 1 FROM detections WHERE image_path = 'seed_stats_angry_emotion.jpg')
BEGIN
    INSERT INTO detections (user_id, image_path, detection_type, objects_detected, confidence_scores, timestamp, processing_time)
    VALUES (
        @admin_id,
        'seed_stats_angry_emotion.jpg',
        'emotion',
        '[{"name": "Giận dữ", "confidence": 0.74, "box": [140, 110, 500, 380]}]',
        '[0.74]',
        DATEADD(DAY, -2, GETUTCDATE()),
        0.049
    );
    PRINT N'[OK] Stats: emotion detection (Giận dữ)';
END

-- Ngày -1: Classification indoor
IF NOT EXISTS (SELECT 1 FROM detections WHERE image_path = 'seed_stats_indoor_class.jpg')
BEGIN
    INSERT INTO detections (user_id, image_path, detection_type, objects_detected, confidence_scores, timestamp, processing_time)
    VALUES (
        @admin_id,
        'seed_stats_indoor_class.jpg',
        'classification',
        '[{"name": "laptop", "confidence": 0.93, "box": [100, 150, 450, 380]}, {"name": "keyboard", "confidence": 0.85, "box": [120, 350, 430, 420]}, {"name": "mouse", "confidence": 0.78, "box": [460, 360, 520, 400]}]',
        '[0.93, 0.85, 0.78]',
        DATEADD(DAY, -1, GETUTCDATE()),
        0.091
    );
    PRINT N'[OK] Stats: classification (laptop + keyboard + mouse)';
END

-- =============================================
-- THỐNG KÊ TỔNG KẾT
-- =============================================
PRINT N'';
PRINT N'========================================';
PRINT N'  SEED STATISTICS DATA COMPLETED';
PRINT N'========================================';

-- Hiển thị tổng quan
SELECT 
    u.username AS [User],
    COUNT(d.id) AS [Total Detections],
    SUM(CASE WHEN d.detection_type = 'upload' THEN 1 ELSE 0 END) AS [Upload],
    SUM(CASE WHEN d.detection_type = 'camera' THEN 1 ELSE 0 END) AS [Camera],
    SUM(CASE WHEN d.detection_type IN ('face_upload', 'face_camera') THEN 1 ELSE 0 END) AS [Face],
    SUM(CASE WHEN d.detection_type = 'color' THEN 1 ELSE 0 END) AS [Color],
    SUM(CASE WHEN d.detection_type = 'emotion' THEN 1 ELSE 0 END) AS [Emotion],
    SUM(CASE WHEN d.detection_type = 'classification' THEN 1 ELSE 0 END) AS [Classification]
FROM users u
LEFT JOIN detections d ON u.id = d.user_id
GROUP BY u.username
ORDER BY [Total Detections] DESC;

PRINT N'========================================';
GO
