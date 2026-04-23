-- data/01_create_database.sql
-- Script để tạo cơ sở dữ liệu VisionAI trên SQL Server

USE master;
GO

-- Kiểm tra và tạo database nếu chưa tồn tại
IF NOT EXISTS (SELECT name FROM sys.databases WHERE name = N'VisionAIDB')
BEGIN
    CREATE DATABASE VisionAIDB;
    PRINT 'Database VisionAIDB created successfully.';
END
ELSE
BEGIN
    PRINT 'Database VisionAIDB already exists.';
END
GO
