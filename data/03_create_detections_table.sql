-- data/03_create_detections_table.sql
-- Script tạo bảng detections trong cơ sở dữ liệu VisionAI

USE VisionAIDB;
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='detections' AND xtype='U')
BEGIN
    CREATE TABLE detections (
        id INT IDENTITY(1,1) PRIMARY KEY,
        user_id INT NOT NULL,
        image_path NVARCHAR(255) NOT NULL,
        detection_type NVARCHAR(20) NOT NULL,
        objects_detected NVARCHAR(MAX) NOT NULL, -- Dùng NVARCHAR(MAX) để lưu JSON cho linh hoạt
        confidence_scores NVARCHAR(MAX) NULL,    -- Dùng NVARCHAR(MAX) để lưu JSON
        timestamp DATETIME DEFAULT GETUTCDATE(),
        processing_time FLOAT NULL,
        CONSTRAINT FK_detections_users FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    );
    PRINT 'Table detections created successfully.';
END
ELSE
BEGIN
    PRINT 'Table detections already exists.';
END
GO
