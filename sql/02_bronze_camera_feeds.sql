-- ============================================
-- BƯỚC 3: BRONZE - Dữ liệu thô từ camera AI
-- Tầng đầu tiên trong kiến trúc Medallion
-- Dữ liệu được giữ nguyên gốc, chưa qua xử lý
-- ============================================

CREATE OR REPLACE TABLE bronze.camera_feeds (
    feed_id         INT,
    camera_id       STRING,
    image_path      STRING,
    capture_time    TIMESTAMP,
    location        STRING,
    file_size_kb    INT,
    resolution      STRING,
    ingested_at     TIMESTAMP DEFAULT current_timestamp()
);

-- Chèn dữ liệu mẫu (giả lập 15 bản ghi từ 3 camera trong 1 ngày)
INSERT INTO bronze.camera_feeds (feed_id, camera_id, image_path, capture_time, location, file_size_kb, resolution)
VALUES
    (1,  'CAM_01', '/feeds/gate_a/img_0801.jpg', '2026-04-21 08:01:00', 'Gate A - Main Entrance',    2048, '1920x1080'),
    (2,  'CAM_01', '/feeds/gate_a/img_0815.jpg', '2026-04-21 08:15:00', 'Gate A - Main Entrance',    2100, '1920x1080'),
    (3,  'CAM_01', '/feeds/gate_a/img_0830.jpg', '2026-04-21 08:30:00', 'Gate A - Main Entrance',    1980, '1920x1080'),
    (4,  'CAM_02', '/feeds/gate_b/img_0805.jpg', '2026-04-21 08:05:00', 'Gate B - Side Entrance',    1850, '1280x720'),
    (5,  'CAM_02', '/feeds/gate_b/img_0820.jpg', '2026-04-21 08:20:00', 'Gate B - Side Entrance',    1900, '1280x720'),
    (6,  'CAM_02', '/feeds/gate_b/img_0900.jpg', '2026-04-21 09:00:00', 'Gate B - Side Entrance',    1750, '1280x720'),
    (7,  'CAM_03', '/feeds/parking/img_0810.jpg', '2026-04-21 08:10:00', 'Parking Lot B2',           3200, '3840x2160'),
    (8,  'CAM_03', '/feeds/parking/img_0825.jpg', '2026-04-21 08:25:00', 'Parking Lot B2',           3100, '3840x2160'),
    (9,  'CAM_03', '/feeds/parking/img_0910.jpg', '2026-04-21 09:10:00', 'Parking Lot B2',           3050, '3840x2160'),
    (10, 'CAM_01', '/feeds/gate_a/img_1000.jpg', '2026-04-21 10:00:00', 'Gate A - Main Entrance',    2200, '1920x1080'),
    (11, 'CAM_01', '/feeds/gate_a/img_1400.jpg', '2026-04-21 14:00:00', 'Gate A - Main Entrance',    2150, '1920x1080'),
    (12, 'CAM_02', '/feeds/gate_b/img_1100.jpg', '2026-04-21 11:00:00', 'Gate B - Side Entrance',    1820, '1280x720'),
    (13, 'CAM_02', '/feeds/gate_b/img_1500.jpg', '2026-04-21 15:00:00', 'Gate B - Side Entrance',    1880, '1280x720'),
    (14, 'CAM_03', '/feeds/parking/img_1200.jpg', '2026-04-21 12:00:00', 'Parking Lot B2',           3300, '3840x2160'),
    (15, 'CAM_03', '/feeds/parking/img_1800.jpg', '2026-04-21 18:00:00', 'Parking Lot B2',           2900, '3840x2160');

-- Kiểm tra kết quả
SELECT * FROM bronze.camera_feeds ORDER BY capture_time;
