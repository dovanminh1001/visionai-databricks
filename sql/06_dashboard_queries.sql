-- ============================================
-- BƯỚC 7: Dashboard Queries
-- Copy từng query vào mỗi Widget của Dashboard
-- ============================================

-- Widget 1: Số lượng ảnh theo Camera (Bar Chart)
-- X: camera_id | Y: total_captures
SELECT camera_id, total_captures
FROM gold.detection_by_camera
ORDER BY total_captures DESC;

-- Widget 2: Phân bố theo Ca làm việc (Pie Chart)
-- Label: time_shift | Value: total_captures
SELECT time_shift, total_captures
FROM gold.detection_by_shift;

-- Widget 3: Hoạt động theo Giờ (Line Chart)
-- X: hour_of_day | Y: total_captures
SELECT hour_of_day, total_captures, active_cameras
FROM gold.hourly_activity
ORDER BY hour_of_day;

-- Widget 4: Chất lượng ảnh theo Camera (Stacked Bar)
-- X: camera_id
SELECT camera_id, high_quality_count, medium_quality_count, low_quality_count
FROM gold.detection_by_camera;

-- Widget 5: Model Performance (Table)
SELECT
    model_name, model_version,
    ROUND(precision_score * 100, 1) AS `Precision%`,
    ROUND(map50 * 100, 1) AS `mAP50%`,
    ROUND(map50_95 * 100, 1) AS `mAP50-95%`,
    training_time, status
FROM gold.ml_experiment_log
ORDER BY map50_95 DESC;
