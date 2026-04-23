-- ============================================
-- BƯỚC 5: GOLD - Dữ liệu tổng hợp cho báo cáo
-- 3 bảng: by_camera, by_shift, hourly_activity
-- ============================================

-- Gold 1: Thống kê theo Camera
CREATE OR REPLACE TABLE gold.detection_by_camera AS
SELECT
    camera_id, location, location_type,
    COUNT(*)                    AS total_captures,
    ROUND(AVG(file_size_kb), 0) AS avg_file_size_kb,
    MIN(capture_time)           AS first_capture,
    MAX(capture_time)           AS last_capture,
    SUM(CASE WHEN quality_bucket = 'HIGH' THEN 1 ELSE 0 END)   AS high_quality_count,
    SUM(CASE WHEN quality_bucket = 'MEDIUM' THEN 1 ELSE 0 END) AS medium_quality_count,
    SUM(CASE WHEN quality_bucket = 'LOW' THEN 1 ELSE 0 END)    AS low_quality_count
FROM silver.camera_processed
GROUP BY camera_id, location, location_type;

-- Gold 2: Thống kê theo Ca làm việc
CREATE OR REPLACE TABLE gold.detection_by_shift AS
SELECT
    time_shift,
    COUNT(*)                    AS total_captures,
    COUNT(DISTINCT camera_id)   AS active_cameras,
    ROUND(AVG(file_size_kb), 0) AS avg_file_size_kb
FROM silver.camera_processed
GROUP BY time_shift
ORDER BY
    CASE time_shift
        WHEN 'MORNING'   THEN 1
        WHEN 'AFTERNOON' THEN 2
        WHEN 'EVENING'   THEN 3
        WHEN 'NIGHT'     THEN 4
    END;

-- Gold 3: Tổng hợp theo giờ (cho biểu đồ)
CREATE OR REPLACE TABLE gold.hourly_activity AS
SELECT
    hour_of_day,
    COUNT(*)                  AS total_captures,
    COUNT(DISTINCT camera_id) AS active_cameras
FROM silver.camera_processed
GROUP BY hour_of_day
ORDER BY hour_of_day;

-- Kiểm tra kết quả Gold
SELECT '--- BY CAMERA ---' AS report;
SELECT * FROM gold.detection_by_camera;
SELECT '--- BY SHIFT ---' AS report;
SELECT * FROM gold.detection_by_shift;
SELECT '--- BY HOUR ---' AS report;
SELECT * FROM gold.hourly_activity;
