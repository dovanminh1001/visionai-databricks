-- ============================================
-- BƯỚC 4: SILVER - Dữ liệu đã xử lý & làm giàu
-- Thêm Feature Engineering: giờ, ca, loại vị trí, chất lượng
-- ============================================

CREATE OR REPLACE TABLE silver.camera_processed AS
SELECT
    feed_id,
    camera_id,
    image_path,
    capture_time,
    location,
    file_size_kb,
    resolution,
    HOUR(capture_time)  AS hour_of_day,
    CASE
        WHEN HOUR(capture_time) BETWEEN 6 AND 11  THEN 'MORNING'
        WHEN HOUR(capture_time) BETWEEN 12 AND 17 THEN 'AFTERNOON'
        WHEN HOUR(capture_time) BETWEEN 18 AND 22 THEN 'EVENING'
        ELSE 'NIGHT'
    END AS time_shift,
    CASE
        WHEN location LIKE '%Gate%'    THEN 'entrance'
        WHEN location LIKE '%Parking%' THEN 'parking'
        WHEN location LIKE '%Lobby%'   THEN 'lobby'
        ELSE 'other'
    END AS location_type,
    CASE
        WHEN file_size_kb >= 3000 THEN 'HIGH'
        WHEN file_size_kb >= 2000 THEN 'MEDIUM'
        ELSE 'LOW'
    END AS quality_bucket,
    current_timestamp() AS processed_at
FROM bronze.camera_feeds;

-- Kiểm tra kết quả Silver
SELECT * FROM silver.camera_processed ORDER BY capture_time;
