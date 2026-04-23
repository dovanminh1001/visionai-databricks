-- data/05_seed_detections.sql
-- Script khởi tạo dữ liệu lịch sử nhận diện mẫu cho ứng dụng VisionAI
-- Mô phỏng các loại detection: object (upload/camera), face, color, emotion, classification
-- Dữ liệu này giúp Dashboard và History hiển thị đầy đủ khi demo

USE VisionAIDB;
GO

-- =============================================
-- Lấy ID của các user đã seed
-- =============================================
DECLARE @admin_id INT, @analyst_id INT, @nguyen_id INT, @tester_id INT;

SELECT @admin_id = id FROM users WHERE username = 'admin';
SELECT @analyst_id = id FROM users WHERE username = 'analyst';
SELECT @nguyen_id = id FROM users WHERE username = 'nguyenvana';
SELECT @tester_id = id FROM users WHERE username = 'tester';

-- Kiểm tra user tồn tại trước khi seed
IF @admin_id IS NULL
BEGIN
    PRINT N'[ERROR] Admin user not found. Run 04_seed_users.sql first!';
    RETURN;
END

-- =============================================
-- DETECTION DATA CHO ADMIN
-- =============================================
-- 1. Object Detection - Upload (YOLO: nhận diện người + xe)
IF NOT EXISTS (SELECT 1 FROM detections WHERE image_path = 'seed_admin_object_01.jpg')
BEGIN
    INSERT INTO detections (user_id, image_path, detection_type, objects_detected, confidence_scores, timestamp, processing_time)
    VALUES (
        @admin_id,
        'seed_admin_object_01.jpg',
        'upload',
        '[{"name": {"en": "person", "vi": "Người"}, "confidence": 0.92, "x1": 120, "y1": 80, "x2": 340, "y2": 450, "class": "person", "bilingual": {"en": "person", "vi": "Người"}}, {"name": {"en": "car", "vi": "Ô tô"}, "confidence": 0.87, "x1": 400, "y1": 200, "x2": 600, "y2": 380, "class": "car", "bilingual": {"en": "car", "vi": "Ô tô"}}, {"name": {"en": "traffic light", "vi": "Đèn giao thông"}, "confidence": 0.78, "x1": 50, "y1": 10, "x2": 100, "y2": 80, "class": "traffic light", "bilingual": {"en": "traffic light", "vi": "Đèn giao thông"}}]',
        '[0.92, 0.87, 0.78]',
        DATEADD(DAY, -28, GETUTCDATE()),
        0.145
    );
    PRINT N'[OK] Admin detection 1: Object Upload (person + car + traffic light)';
END

-- 2. Object Detection - Camera (YOLO: nhận diện laptop + phone)
IF NOT EXISTS (SELECT 1 FROM detections WHERE image_path = 'seed_admin_camera_01.jpg')
BEGIN
    INSERT INTO detections (user_id, image_path, detection_type, objects_detected, confidence_scores, timestamp, processing_time)
    VALUES (
        @admin_id,
        'seed_admin_camera_01.jpg',
        'camera',
        '[{"en": "laptop", "vi": "Máy tính xách tay"}, {"en": "cell phone", "vi": "Điện thoại"}, {"en": "cup", "vi": "Cốc"}]',
        '[0.94, 0.88, 0.72]',
        DATEADD(DAY, -25, GETUTCDATE()),
        0.098
    );
    PRINT N'[OK] Admin detection 2: Camera (laptop + phone + cup)';
END

-- 3. Face Detection - Upload
IF NOT EXISTS (SELECT 1 FROM detections WHERE image_path = 'seed_admin_face_01.jpg')
BEGIN
    INSERT INTO detections (user_id, image_path, detection_type, objects_detected, confidence_scores, timestamp, processing_time)
    VALUES (
        @admin_id,
        'seed_admin_face_01.jpg',
        'face_upload',
        '[{"box": [150, 80, 200, 220], "confidence": 0.95, "name": "Admin"}, {"box": [400, 90, 180, 210], "confidence": 0.88, "name": "Unknown"}]',
        '[0.95, 0.88]',
        DATEADD(DAY, -22, GETUTCDATE()),
        0.067
    );
    PRINT N'[OK] Admin detection 3: Face Upload (2 faces)';
END

-- 4. Color Detection
IF NOT EXISTS (SELECT 1 FROM detections WHERE image_path = 'seed_admin_color_01.jpg')
BEGIN
    INSERT INTO detections (user_id, image_path, detection_type, objects_detected, confidence_scores, timestamp, processing_time)
    VALUES (
        @admin_id,
        'seed_admin_color_01.jpg',
        'color',
        '[{"rgb": [41, 128, 185], "hex": "#2980b9", "name": "Blue", "percentage": 35.42}, {"rgb": [236, 240, 241], "hex": "#ecf0f1", "name": "White", "percentage": 28.15}, {"rgb": [44, 62, 80], "hex": "#2c3e50", "name": "Dark Gray", "percentage": 18.73}, {"rgb": [39, 174, 96], "hex": "#27ae60", "name": "Green", "percentage": 10.85}, {"rgb": [231, 76, 60], "hex": "#e74c3c", "name": "Red", "percentage": 6.85}]',
        '[35.42, 28.15, 18.73, 10.85, 6.85]',
        DATEADD(DAY, -18, GETUTCDATE()),
        0.034
    );
    PRINT N'[OK] Admin detection 4: Color Detection (5 colors)';
END

-- 5. Emotion Detection
IF NOT EXISTS (SELECT 1 FROM detections WHERE image_path = 'seed_admin_emotion_01.jpg')
BEGIN
    INSERT INTO detections (user_id, image_path, detection_type, objects_detected, confidence_scores, timestamp, processing_time)
    VALUES (
        @admin_id,
        'seed_admin_emotion_01.jpg',
        'emotion',
        '[{"name": "Vui vẻ", "confidence": 0.85, "box": [160, 120, 480, 360]}]',
        '[0.85]',
        DATEADD(DAY, -15, GETUTCDATE()),
        0.052
    );
    PRINT N'[OK] Admin detection 5: Emotion Detection (Vui vẻ)';
END

-- 6. Classification
IF NOT EXISTS (SELECT 1 FROM detections WHERE image_path = 'seed_admin_class_01.jpg')
BEGIN
    INSERT INTO detections (user_id, image_path, detection_type, objects_detected, confidence_scores, timestamp, processing_time)
    VALUES (
        @admin_id,
        'seed_admin_class_01.jpg',
        'classification',
        '[{"name": "dog", "confidence": 0.91, "box": [50, 100, 400, 350]}, {"name": "person", "confidence": 0.82, "box": [420, 60, 600, 440]}]',
        '[0.91, 0.82]',
        DATEADD(DAY, -12, GETUTCDATE()),
        0.078
    );
    PRINT N'[OK] Admin detection 6: Classification (dog + person)';
END

-- =============================================
-- DETECTION DATA CHO ANALYST
-- =============================================
IF @analyst_id IS NOT NULL
BEGIN
    -- 7. Object Detection - Upload (nhiều đối tượng)
    IF NOT EXISTS (SELECT 1 FROM detections WHERE image_path = 'seed_analyst_object_01.jpg')
    BEGIN
        INSERT INTO detections (user_id, image_path, detection_type, objects_detected, confidence_scores, timestamp, processing_time)
        VALUES (
            @analyst_id,
            'seed_analyst_object_01.jpg',
            'upload',
            '[{"name": {"en": "motorcycle", "vi": "Xe máy"}, "confidence": 0.93, "x1": 50, "y1": 150, "x2": 300, "y2": 400, "class": "motorcycle", "bilingual": {"en": "motorcycle", "vi": "Xe máy"}}, {"name": {"en": "person", "vi": "Người"}, "confidence": 0.89, "x1": 100, "y1": 50, "x2": 280, "y2": 380, "class": "person", "bilingual": {"en": "person", "vi": "Người"}}, {"name": {"en": "backpack", "vi": "Balo"}, "confidence": 0.74, "x1": 150, "y1": 80, "x2": 250, "y2": 200, "class": "backpack", "bilingual": {"en": "backpack", "vi": "Balo"}}, {"name": {"en": "umbrella", "vi": "Ô"}, "confidence": 0.68, "x1": 80, "y1": 20, "x2": 220, "y2": 120, "class": "umbrella", "bilingual": {"en": "umbrella", "vi": "Ô"}}]',
            '[0.93, 0.89, 0.74, 0.68]',
            DATEADD(DAY, -18, GETUTCDATE()),
            0.167
        );
        PRINT N'[OK] Analyst detection 1: Object Upload (motorcycle + person + backpack + umbrella)';
    END

    -- 8. Face Detection - Camera
    IF NOT EXISTS (SELECT 1 FROM detections WHERE image_path = 'seed_analyst_face_01.jpg')
    BEGIN
        INSERT INTO detections (user_id, image_path, detection_type, objects_detected, confidence_scores, timestamp, processing_time)
        VALUES (
            @analyst_id,
            'seed_analyst_face_01.jpg',
            'face_camera',
            '[{"box": [100, 60, 180, 200], "confidence": 0.97, "name": "Unknown"}, {"box": [320, 70, 170, 190], "confidence": 0.93, "name": "Unknown"}, {"box": [540, 80, 160, 180], "confidence": 0.86, "name": "Unknown"}]',
            '[0.97, 0.93, 0.86]',
            DATEADD(DAY, -14, GETUTCDATE()),
            0.089
        );
        PRINT N'[OK] Analyst detection 2: Face Camera (3 faces)';
    END

    -- 9. Color Detection
    IF NOT EXISTS (SELECT 1 FROM detections WHERE image_path = 'seed_analyst_color_01.jpg')
    BEGIN
        INSERT INTO detections (user_id, image_path, detection_type, objects_detected, confidence_scores, timestamp, processing_time)
        VALUES (
            @analyst_id,
            'seed_analyst_color_01.jpg',
            'color',
            '[{"rgb": [192, 57, 43], "hex": "#c0392b", "name": "Red", "percentage": 42.30}, {"rgb": [243, 156, 18], "hex": "#f39c12", "name": "Orange", "percentage": 22.10}, {"rgb": [255, 255, 255], "hex": "#ffffff", "name": "White", "percentage": 15.60}, {"rgb": [52, 73, 94], "hex": "#34495e", "name": "Dark Gray", "percentage": 12.50}, {"rgb": [46, 204, 113], "hex": "#2ecc71", "name": "Green", "percentage": 7.50}]',
            '[42.30, 22.10, 15.60, 12.50, 7.50]',
            DATEADD(DAY, -10, GETUTCDATE()),
            0.041
        );
        PRINT N'[OK] Analyst detection 3: Color Detection (5 colors)';
    END

    -- 10. Emotion Detection
    IF NOT EXISTS (SELECT 1 FROM detections WHERE image_path = 'seed_analyst_emotion_01.jpg')
    BEGIN
        INSERT INTO detections (user_id, image_path, detection_type, objects_detected, confidence_scores, timestamp, processing_time)
        VALUES (
            @analyst_id,
            'seed_analyst_emotion_01.jpg',
            'emotion',
            '[{"name": "Ngạc nhiên", "confidence": 0.72, "box": [140, 100, 500, 380]}]',
            '[0.72]',
            DATEADD(DAY, -7, GETUTCDATE()),
            0.061
        );
        PRINT N'[OK] Analyst detection 4: Emotion Detection (Ngạc nhiên)';
    END

    -- 11. Object Detection - Camera (animal scene)
    IF NOT EXISTS (SELECT 1 FROM detections WHERE image_path = 'seed_analyst_camera_01.jpg')
    BEGIN
        INSERT INTO detections (user_id, image_path, detection_type, objects_detected, confidence_scores, timestamp, processing_time)
        VALUES (
            @analyst_id,
            'seed_analyst_camera_01.jpg',
            'camera',
            '[{"en": "dog", "vi": "Chó"}, {"en": "cat", "vi": "Mèo"}, {"en": "couch", "vi": "Sô pha"}]',
            '[0.91, 0.84, 0.76]',
            DATEADD(DAY, -3, GETUTCDATE()),
            0.112
        );
        PRINT N'[OK] Analyst detection 5: Camera (dog + cat + couch)';
    END
END
ELSE
    PRINT N'[SKIP] Analyst user not found, skipping analyst detections.';
GO

-- =============================================
-- DETECTION DATA CHO NGUYENVANA
-- =============================================
DECLARE @nguyen_id2 INT;
SELECT @nguyen_id2 = id FROM users WHERE username = 'nguyenvana';

IF @nguyen_id2 IS NOT NULL
BEGIN
    -- 12. Object Detection - Upload (food scene)
    IF NOT EXISTS (SELECT 1 FROM detections WHERE image_path = 'seed_nguyen_object_01.jpg')
    BEGIN
        INSERT INTO detections (user_id, image_path, detection_type, objects_detected, confidence_scores, timestamp, processing_time)
        VALUES (
            @nguyen_id2,
            'seed_nguyen_object_01.jpg',
            'upload',
            '[{"name": {"en": "pizza", "vi": "Pizza"}, "confidence": 0.96, "x1": 80, "y1": 100, "x2": 450, "y2": 380, "class": "pizza", "bilingual": {"en": "pizza", "vi": "Pizza"}}, {"name": {"en": "bottle", "vi": "Chai"}, "confidence": 0.85, "x1": 500, "y1": 50, "x2": 560, "y2": 300, "class": "bottle", "bilingual": {"en": "bottle", "vi": "Chai"}}, {"name": {"en": "dining table", "vi": "Bàn ăn"}, "confidence": 0.79, "x1": 0, "y1": 80, "x2": 640, "y2": 480, "class": "dining table", "bilingual": {"en": "dining table", "vi": "Bàn ăn"}}]',
            '[0.96, 0.85, 0.79]',
            DATEADD(DAY, -8, GETUTCDATE()),
            0.134
        );
        PRINT N'[OK] NguyenVanA detection 1: Object Upload (pizza + bottle + dining table)';
    END

    -- 13. Face Detection - Upload
    IF NOT EXISTS (SELECT 1 FROM detections WHERE image_path = 'seed_nguyen_face_01.jpg')
    BEGIN
        INSERT INTO detections (user_id, image_path, detection_type, objects_detected, confidence_scores, timestamp, processing_time)
        VALUES (
            @nguyen_id2,
            'seed_nguyen_face_01.jpg',
            'face_upload',
            '[{"box": [200, 100, 220, 240], "confidence": 0.94, "name": "Unknown"}]',
            '[0.94]',
            DATEADD(DAY, -6, GETUTCDATE()),
            0.055
        );
        PRINT N'[OK] NguyenVanA detection 2: Face Upload (1 face)';
    END

    -- 14. Color Detection (sunset colors)
    IF NOT EXISTS (SELECT 1 FROM detections WHERE image_path = 'seed_nguyen_color_01.jpg')
    BEGIN
        INSERT INTO detections (user_id, image_path, detection_type, objects_detected, confidence_scores, timestamp, processing_time)
        VALUES (
            @nguyen_id2,
            'seed_nguyen_color_01.jpg',
            'color',
            '[{"rgb": [230, 126, 34], "hex": "#e67e22", "name": "Orange", "percentage": 38.90}, {"rgb": [241, 196, 15], "hex": "#f1c40f", "name": "Yellow-Orange", "percentage": 25.20}, {"rgb": [155, 89, 182], "hex": "#9b59b6", "name": "Purple", "percentage": 18.40}, {"rgb": [52, 73, 94], "hex": "#34495e", "name": "Dark Gray", "percentage": 11.30}, {"rgb": [236, 240, 241], "hex": "#ecf0f1", "name": "Light Gray", "percentage": 6.20}]',
            '[38.90, 25.20, 18.40, 11.30, 6.20]',
            DATEADD(DAY, -4, GETUTCDATE()),
            0.038
        );
        PRINT N'[OK] NguyenVanA detection 3: Color Detection (sunset palette)';
    END

    -- 15. Emotion Detection
    IF NOT EXISTS (SELECT 1 FROM detections WHERE image_path = 'seed_nguyen_emotion_01.jpg')
    BEGIN
        INSERT INTO detections (user_id, image_path, detection_type, objects_detected, confidence_scores, timestamp, processing_time)
        VALUES (
            @nguyen_id2,
            'seed_nguyen_emotion_01.jpg',
            'emotion',
            '[{"name": "Bình thường", "confidence": 0.62, "box": [150, 110, 490, 370]}]',
            '[0.62]',
            DATEADD(DAY, -2, GETUTCDATE()),
            0.048
        );
        PRINT N'[OK] NguyenVanA detection 4: Emotion Detection (Bình thường)';
    END

    -- 16. Object Detection - Camera (indoor)
    IF NOT EXISTS (SELECT 1 FROM detections WHERE image_path = 'seed_nguyen_camera_01.jpg')
    BEGIN
        INSERT INTO detections (user_id, image_path, detection_type, objects_detected, confidence_scores, timestamp, processing_time)
        VALUES (
            @nguyen_id2,
            'seed_nguyen_camera_01.jpg',
            'camera',
            '[{"en": "chair", "vi": "Cái ghế"}, {"en": "potted plant", "vi": "Cây cảnh"}, {"en": "book", "vi": "Sách"}, {"en": "clock", "vi": "Đồng hồ"}]',
            '[0.88, 0.82, 0.75, 0.69]',
            DATEADD(DAY, -1, GETUTCDATE()),
            0.105
        );
        PRINT N'[OK] NguyenVanA detection 5: Camera (chair + plant + book + clock)';
    END
END
ELSE
    PRINT N'[SKIP] NguyenVanA user not found, skipping detections.';
GO

-- =============================================
-- DETECTION DATA CHO TESTER
-- =============================================
DECLARE @tester_id2 INT;
SELECT @tester_id2 = id FROM users WHERE username = 'tester';

IF @tester_id2 IS NOT NULL
BEGIN
    -- 17. Object Detection - Upload (vehicle scene)
    IF NOT EXISTS (SELECT 1 FROM detections WHERE image_path = 'seed_tester_object_01.jpg')
    BEGIN
        INSERT INTO detections (user_id, image_path, detection_type, objects_detected, confidence_scores, timestamp, processing_time)
        VALUES (
            @tester_id2,
            'seed_tester_object_01.jpg',
            'upload',
            '[{"name": {"en": "bus", "vi": "Xe buýt"}, "confidence": 0.90, "x1": 30, "y1": 100, "x2": 500, "y2": 420, "class": "bus", "bilingual": {"en": "bus", "vi": "Xe buýt"}}, {"name": {"en": "person", "vi": "Người"}, "confidence": 0.86, "x1": 520, "y1": 150, "x2": 600, "y2": 400, "class": "person", "bilingual": {"en": "person", "vi": "Người"}}, {"name": {"en": "bicycle", "vi": "Xe đạp"}, "confidence": 0.71, "x1": 350, "y1": 300, "x2": 480, "y2": 450, "class": "bicycle", "bilingual": {"en": "bicycle", "vi": "Xe đạp"}}]',
            '[0.90, 0.86, 0.71]',
            DATEADD(DAY, -4, GETUTCDATE()),
            0.155
        );
        PRINT N'[OK] Tester detection 1: Object Upload (bus + person + bicycle)';
    END

    -- 18. Classification
    IF NOT EXISTS (SELECT 1 FROM detections WHERE image_path = 'seed_tester_class_01.jpg')
    BEGIN
        INSERT INTO detections (user_id, image_path, detection_type, objects_detected, confidence_scores, timestamp, processing_time)
        VALUES (
            @tester_id2,
            'seed_tester_class_01.jpg',
            'classification',
            '[{"name": "cat", "confidence": 0.88, "box": [80, 120, 350, 400]}, {"name": "couch", "confidence": 0.73, "box": [0, 200, 640, 480]}]',
            '[0.88, 0.73]',
            DATEADD(DAY, -3, GETUTCDATE()),
            0.082
        );
        PRINT N'[OK] Tester detection 2: Classification (cat + couch)';
    END

    -- 19. Emotion Detection (sad)
    IF NOT EXISTS (SELECT 1 FROM detections WHERE image_path = 'seed_tester_emotion_01.jpg')
    BEGIN
        INSERT INTO detections (user_id, image_path, detection_type, objects_detected, confidence_scores, timestamp, processing_time)
        VALUES (
            @tester_id2,
            'seed_tester_emotion_01.jpg',
            'emotion',
            '[{"name": "Buồn bã", "confidence": 0.68, "box": [160, 130, 470, 350]}]',
            '[0.68]',
            DATEADD(DAY, -1, GETUTCDATE()),
            0.057
        );
        PRINT N'[OK] Tester detection 3: Emotion Detection (Buồn bã)';
    END
END
ELSE
    PRINT N'[SKIP] Tester user not found, skipping detections.';
GO

-- =============================================
-- THỐNG KÊ KẾT QUẢ
-- =============================================
PRINT N'';
PRINT N'========================================';
PRINT N'  SEED DETECTIONS COMPLETED';
PRINT N'========================================';

SELECT 
    u.username,
    u.role,
    COUNT(d.id) AS total_detections,
    STRING_AGG(DISTINCT d.detection_type, ', ') AS detection_types
FROM users u
LEFT JOIN detections d ON u.id = d.user_id
GROUP BY u.username, u.role
ORDER BY u.role DESC, total_detections DESC;

PRINT N'========================================';
GO
