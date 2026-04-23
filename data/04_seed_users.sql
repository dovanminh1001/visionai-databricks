-- data/04_seed_users.sql
-- Script khởi tạo tài khoản người dùng cho ứng dụng VisionAI
-- Bao gồm: Admin, Analyst (phân tích viên), và Regular Users (người dùng thường)
-- Tất cả password hash được sinh bởi werkzeug.security.generate_password_hash (Python)

USE VisionAIDB;
GO

-- =============================================
-- 1. TÀI KHOẢN ADMIN - Quản trị hệ thống
-- =============================================
IF NOT EXISTS (SELECT 1 FROM users WHERE username = 'admin')
BEGIN
    INSERT INTO users (email, username, password_hash, role, is_active, created_at, birth_date, location)
    VALUES (
        'admin@visionai.com',
        'admin',
        'pbkdf2:sha256:600000$I9aPwiHzacjm5I14$1e42df90c142e944c7da7c98891c3d2755ace99423404e91fffce8a749f20ef9',
        'admin',
        1,
        DATEADD(DAY, -30, GETUTCDATE()),  -- Tạo trước 30 ngày
        '1995-06-15',
        N'TP. Hồ Chí Minh'
    );
    PRINT N'[OK] Admin account created: admin@visionai.com / admin123';
END
ELSE
BEGIN
    UPDATE users SET password_hash = 'pbkdf2:sha256:600000$I9aPwiHzacjm5I14$1e42df90c142e944c7da7c98891c3d2755ace99423404e91fffce8a749f20ef9' WHERE username = 'admin';
    PRINT N'[OK] Admin account password updated.';
END
GO

-- =============================================
-- 2. TÀI KHOẢN ANALYST - Phân tích viên AI
-- =============================================
IF NOT EXISTS (SELECT 1 FROM users WHERE username = 'analyst')
BEGIN
    INSERT INTO users (email, username, password_hash, role, is_active, created_at, birth_date, location)
    VALUES (
        'analyst@visionai.com',
        'analyst',
        'pbkdf2:sha256:600000$bQQ7v5mcQ8RHz7uL$0c411a59dc05e7bd7012d70c9031a94cdcc101e33ab6dbab77df7e81b5a88430',
        'user',
        1,
        DATEADD(DAY, -20, GETUTCDATE()),  -- Tạo trước 20 ngày
        '1998-03-22',
        N'Hà Nội'
    );
    PRINT N'[OK] Analyst account created: analyst@visionai.com / analyst123';
END
ELSE
BEGIN
    UPDATE users SET password_hash = 'pbkdf2:sha256:600000$bQQ7v5mcQ8RHz7uL$0c411a59dc05e7bd7012d70c9031a94cdcc101e33ab6dbab77df7e81b5a88430' WHERE username = 'analyst';
    PRINT N'[OK] Analyst account password updated.';
END
GO

-- =============================================
-- 3. TÀI KHOẢN NGƯỜI DÙNG - Nguyễn Văn A
-- =============================================
IF NOT EXISTS (SELECT 1 FROM users WHERE username = 'nguyenvana')
BEGIN
    INSERT INTO users (email, username, password_hash, role, is_active, created_at, birth_date, location)
    VALUES (
        'nguyenvana@gmail.com',
        'nguyenvana',
        'pbkdf2:sha256:600000$p2veGQycpzkU1et3$5f63739277d1a460d0c03a99bafbdab8fbd19cd201e403a2ad1a327ea1240ed3',
        'user',
        1,
        DATEADD(DAY, -10, GETUTCDATE()),  -- Tạo trước 10 ngày
        '2000-11-08',
        N'Đà Nẵng'
    );
    PRINT N'[OK] User account created: nguyenvana@gmail.com / nguyen123';
END
ELSE
BEGIN
    UPDATE users SET password_hash = 'pbkdf2:sha256:600000$p2veGQycpzkU1et3$5f63739277d1a460d0c03a99bafbdab8fbd19cd201e403a2ad1a327ea1240ed3' WHERE username = 'nguyenvana';
    PRINT N'[OK] User nguyenvana password updated.';
END
GO

-- =============================================
-- 4. TÀI KHOẢN TESTER - Dùng để kiểm thử
-- =============================================
IF NOT EXISTS (SELECT 1 FROM users WHERE username = 'tester')
BEGIN
    INSERT INTO users (email, username, password_hash, role, is_active, created_at, birth_date, location)
    VALUES (
        'tester@visionai.com',
        'tester',
        'pbkdf2:sha256:600000$3gLvoHD3OACvDT99$912dd8e3d22bdd8d60a88db6707f493a807c304dc4e070fa160a2bb2c7dd83c2',
        'user',
        1,
        DATEADD(DAY, -5, GETUTCDATE()),  -- Tạo trước 5 ngày
        '2001-07-30',
        N'Cần Thơ'
    );
    PRINT N'[OK] Tester account created: tester@visionai.com / tester123';
END
ELSE
BEGIN
    UPDATE users SET password_hash = 'pbkdf2:sha256:600000$3gLvoHD3OACvDT99$912dd8e3d22bdd8d60a88db6707f493a807c304dc4e070fa160a2bb2c7dd83c2' WHERE username = 'tester';
    PRINT N'[OK] Tester account password updated.';
END
GO

-- =============================================
-- 5. TÀI KHOẢN DEMO - Tài khoản trình diễn
-- =============================================
IF NOT EXISTS (SELECT 1 FROM users WHERE username = 'demo')
BEGIN
    INSERT INTO users (email, username, password_hash, role, is_active, created_at, birth_date, location)
    VALUES (
        'demo@visionai.com',
        'demo',
        'pbkdf2:sha256:600000$06Af1kVHF32xPZia$f238fe712a3322781ad0134293521c09631e86ea31817679168da6b0107f730a',
        'user',
        1,
        DATEADD(DAY, -2, GETUTCDATE()),  -- Tạo trước 2 ngày
        NULL,
        N'Việt Nam'
    );
    PRINT N'[OK] Demo account created: demo@visionai.com / demo123';
END
ELSE
BEGIN
    UPDATE users SET password_hash = 'pbkdf2:sha256:600000$06Af1kVHF32xPZia$f238fe712a3322781ad0134293521c09631e86ea31817679168da6b0107f730a' WHERE username = 'demo';
    PRINT N'[OK] Demo account password updated.';
END
GO

-- =============================================
-- BẢNG TÓM TẮT TÀI KHOẢN
-- =============================================
-- | Username    | Email                  | Password    | Role  |
-- |-------------|------------------------|-------------|-------|
-- | admin       | admin@visionai.com     | admin123    | admin |
-- | analyst     | analyst@visionai.com   | analyst123  | user  |
-- | nguyenvana  | nguyenvana@gmail.com   | nguyen123   | user  |
-- | tester      | tester@visionai.com    | tester123   | user  |
-- | demo        | demo@visionai.com      | demo123     | user  |
-- =============================================

PRINT N'';
PRINT N'========================================';
PRINT N'  SEED USERS COMPLETED SUCCESSFULLY';
PRINT N'========================================';
GO
