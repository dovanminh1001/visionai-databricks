-- ============================================
-- BƯỚC 2: Tạo 3 Schema cho Medallion Architecture
-- Chạy đầu tiên trên Databricks SQL Editor
-- ============================================

-- Tạo 3 Schema cho kiến trúc Medallion
CREATE SCHEMA IF NOT EXISTS bronze;
CREATE SCHEMA IF NOT EXISTS silver;
CREATE SCHEMA IF NOT EXISTS gold;
