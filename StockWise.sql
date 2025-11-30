DROP DATABASE IF EXISTS StockWise;
CREATE DATABASE StockWise CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE StockWise;

-- 1. Bảng Nhân Viên
CREATE TABLE NhanVien (
    ma_nhan_vien VARCHAR(20) PRIMARY KEY,
    ho_ten VARCHAR(100) NOT NULL,
    chuc_vu VARCHAR(50),
    ngay_vao_lam DATE,
    luong_co_ban DECIMAL(15, 0),
    so_don_da_ban INT DEFAULT 0
);

-- 2. Bảng Tài Khoản (Đăng nhập)
CREATE TABLE TaiKhoan (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ten_dang_nhap VARCHAR(50) NOT NULL UNIQUE,
    mat_khau VARCHAR(255) NOT NULL,
    ma_nhan_vien VARCHAR(20),
    FOREIGN KEY (ma_nhan_vien) REFERENCES NhanVien(ma_nhan_vien) ON DELETE CASCADE
);

-- 3. Bảng Khách Hàng
CREATE TABLE KhachHang (
    ma_khach_hang VARCHAR(20) PRIMARY KEY,
    ho_ten VARCHAR(100) NOT NULL,
    so_dien_thoai VARCHAR(20),
    dia_chi VARCHAR(255)
);

-- 4. Bảng Sản Phẩm
CREATE TABLE SanPham (
    ma_san_pham VARCHAR(20) PRIMARY KEY,
    ten_san_pham VARCHAR(255) NOT NULL,
    danh_muc VARCHAR(50),
    gia_ban DECIMAL(15, 0) NOT NULL,
    so_luong_ton INT DEFAULT 0,
    hinh_anh TEXT -- Lưu đường dẫn ảnh
);

-- 5. Bảng Hóa Đơn
CREATE TABLE HoaDon (
    ma_hoa_don INT AUTO_INCREMENT PRIMARY KEY,
    ngay_lap DATETIME DEFAULT CURRENT_TIMESTAMP,
    tong_tien DECIMAL(15, 0) NOT NULL,
    ma_nhan_vien VARCHAR(20),
    ma_khach_hang VARCHAR(20),
    FOREIGN KEY (ma_nhan_vien) REFERENCES NhanVien(ma_nhan_vien) ON DELETE SET NULL,
    FOREIGN KEY (ma_khach_hang) REFERENCES KhachHang(ma_khach_hang) ON DELETE SET NULL
);

-- DỮ LIỆU MẪU ĐỂ TEST
INSERT INTO NhanVien VALUES 
('NV01', 'Admin Quản Lý', 'Quản lý', '2020-01-01', 20000000, 0),
('NV02', 'Phạm Nhân Viên', 'Sale', '2023-05-15', 8000000, 0);

INSERT INTO TaiKhoan (ten_dang_nhap, mat_khau, ma_nhan_vien) VALUES 
('admin', '123', 'NV01'),
('thinh', '1', 'NV02');

INSERT INTO KhachHang VALUES 
('KH01', 'Khách vãng lai', '0000000000', 'N/A'),
('KH02', 'Nguyễn Văn An', '0909123456', 'Hà Nội');

INSERT INTO SanPham VALUES 
('SP01', 'Laptop Gaming Dell', 'Laptop', 25000000, 10, ''),
('SP02', 'Chuột Logitech G304', 'Phụ kiện', 850000, 50, '');
select * from TaiKhoan