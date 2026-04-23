-- data/02_create_users_table.sql
-- Script tạo bảng users trong cơ sở dữ liệu VisionAI

USE VisionAIDB;
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='users' AND xtype='U')
BEGIN
    CREATE TABLE users (
        id INT IDENTITY(1,1) PRIMARY KEY,
        email NVARCHAR(120) NOT NULL UNIQUE,
        username NVARCHAR(80) NOT NULL UNIQUE,
        password_hash NVARCHAR(255) NOT NULL,
        role NVARCHAR(20) DEFAULT 'user',
        is_active BIT DEFAULT 1,
        created_at DATETIME DEFAULT GETUTCDATE(),
        last_login DATETIME NULL,
        birth_date DATE NULL,
        location NVARCHAR(200) NULL
    );
    PRINT 'Table users created successfully.';
END
ELSE
BEGIN
    PRINT 'Table users already exists.';
END
GO
