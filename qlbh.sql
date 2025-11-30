drop database qlbanhang;
CREATE DATABASE IF NOT EXISTS QLBANHANG
CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE QLBANHANG;

--- Bảng 1: TaiKhoanQuanTri (Dùng cho đăng nhập hệ thống/Admin) ---
CREATE TABLE IF NOT EXISTS `TaiKhoanQuanTri` (
  `id_quan_tri` INT NOT NULL AUTO_INCREMENT,
  `ten_dang_nhap` VARCHAR(50) NOT NULL UNIQUE,
  `mat_khau_hash` VARCHAR(255) NOT NULL,
  `ho_ten` VARCHAR(100) NULL,
  `vai_tro` ENUM('admin', 'manager', 'accountant') NOT NULL DEFAULT 'manager',
  `ngay_tao` TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_quan_tri`)
) ENGINE=InnoDB;


--- Bảng 2: KhachHang  ---
CREATE TABLE IF NOT EXISTS `KhachHang` (
  `ma_khach_hang` VARCHAR(10) NOT NULL UNIQUE,
  `ho_ten` VARCHAR(100) NOT NULL,
  `so_dien_thoai` VARCHAR(15) NOT NULL UNIQUE,
  `hang_thanh_vien` ENUM('Đồng', 'Bạc', 'VIP') NOT NULL DEFAULT 'Đồng',
  `dia_chi` varchar(100) not null,
  PRIMARY KEY (`ma_khach_hang`)
) ENGINE=InnoDB;


--- Bảng 3: NhanVien ---
CREATE TABLE IF NOT EXISTS `NhanVien` (
  `ma_nhan_vien` VARCHAR(10) NOT NULL UNIQUE COMMENT 'Mã nhân viên (VD: NV001)',
  `ho_ten` VARCHAR(100) NOT NULL,
  `so_dien_thoai` VARCHAR(15) NOT NULL UNIQUE,
  `chuc_vu` VARCHAR(50) NOT NULL DEFAULT 'Nhân viên bán hàng', 
  `ngay_vao_lam` DATE NOT NULL,
  PRIMARY KEY (`ma_nhan_vien`)
) ENGINE=InnoDB;
--- Bảng 4: SanPham ---
CREATE TABLE IF NOT EXISTS `SanPham` (
  `ma_san_pham` VARCHAR(20) NOT NULL UNIQUE COMMENT 'Mã SKU/BarCode của sản phẩm',
  `ten_san_pham` VARCHAR(255) NOT NULL,
  `don_vi_tinh` VARCHAR(20) NOT NULL COMMENT 'VD: Cái, Chiếc, Hộp...',
  `gia_ban` DECIMAL(12, 0) NOT NULL,
  `so_luong_ton` INT NOT NULL DEFAULT 0,
  `trang_thai` ENUM('Đang bán', 'Ngừng kinh doanh', 'Hết hàng') NOT NULL DEFAULT 'Đang bán',
  `ma_nhan_vien_quan_ly` VARCHAR(10) NULL COMMENT 'Nhân viên chịu trách nhiệm quản lý kho',
  PRIMARY KEY (`ma_san_pham`),
  INDEX `fk_SanPham_NhanVien_idx` (`ma_nhan_vien_quan_ly` ASC) VISIBLE,
  CONSTRAINT `fk_SanPham_NhanVien`
    FOREIGN KEY (`ma_nhan_vien_quan_ly`)
    REFERENCES `NhanVien` (`ma_nhan_vien`)
    ON DELETE SET NULL
    ON UPDATE CASCADE
) ENGINE=InnoDB;


--- Bảng 5: HoaDon ---
CREATE TABLE IF NOT EXISTS `HoaDon` (
  `id_hoa_don` INT NOT NULL AUTO_INCREMENT,
  `ma_khach_hang` VARCHAR(10) NOT NULL UNIQUE,
  `ma_nhan_vien` VARCHAR(10) NOT NULL COMMENT 'Nhân viên thực hiện giao dịch', 
  `ma_san_pham` VARCHAR(20) NOT NULL UNIQUE,
  `ten_san_pham` VARCHAR(255) NOT NULL,
  `ngay_lap_hoa_don` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  
  `tong_tien_phai_tra` DECIMAL(12, 0) NOT NULL,
  `tien_khach_thanh_toan` DECIMAL(12, 0) NOT NULL,
  `phuong_thuc_thanh_toan` ENUM('Tiền mặt', 'Chuyển khoản', 'Thẻ', 'Ví điện tử') NOT NULL DEFAULT 'Tiền mặt',
  `trang_thai_thanh_toan` ENUM('Đã thanh toán', 'Chưa thanh toán', 'Đã hủy') NOT NULL DEFAULT 'Đã thanh toán',
  
  PRIMARY KEY (`id_hoa_don`),
  
  INDEX `fk_HoaDon_KhachHang_idx` (`ma_khach_hang` ASC) VISIBLE,
  INDEX `fk_HoaDon_NhanVien_idx` (`ma_nhan_vien` ASC) VISIBLE,
  
  CONSTRAINT `fk_HoaDon_KhachHang`
    FOREIGN KEY (`ma_khach_hang`)
    REFERENCES `KhachHang` (`ma_khach_hang`)
    ON DELETE NO ACTION  
    ON UPDATE CASCADE,
    
  CONSTRAINT `fk_HoaDon_NhanVien`
    FOREIGN KEY (`ma_nhan_vien`)
    REFERENCES `NhanVien` (`ma_nhan_vien`)
    ON DELETE NO ACTION  
    ON UPDATE CASCADE
    
) ENGINE=InnoDB;


--- Dữ liệu Tài khoản Quản trị ---
INSERT INTO `TaiKhoanQuanTri` (`ten_dang_nhap`, `mat_khau_hash`, `ho_ten`, `vai_tro`) 
VALUES 
('admin', '202cb962ac59075b964b07152d234b70', 'Quản Trị Viên Chính', 'admin'),
('manager01', '202cb962ac59075b964b07152d234b70', 'Nguyễn Huỳnh Ngọc Thịnh', 'manager')
ON DUPLICATE KEY UPDATE mat_khau_hash='202cb962ac59075b964b07152d234b70';


--- Dữ liệu Nhân viên ---
INSERT INTO `NhanVien` (`ma_nhan_vien`, `ho_ten`, `so_dien_thoai`, `chuc_vu`, `ngay_vao_lam`)
VALUES
('NV001', 'Nguyễn Văn An', '0901234567', 'Quản lý Kho', '2025-10-04'),
('NV002', 'Trần Văn Bình', '0912345678', 'Nhân viên bán hàng', '2023-06-12'),
('NV003', 'Lê Thị Cẩm', '0923456789', 'Kế toán', '2023-12-22')
ON DUPLICATE KEY UPDATE ma_nhan_vien=ma_nhan_vien;


--- Dữ liệu Khách hàng (Tái sử dụng) ---
INSERT INTO `KhachHang` (`ma_khach_hang`,`ho_ten`, `so_dien_thoai`, `hang_thanh_vien`, `dia_chi`)
VALUES
('C001','Nguyễn Thị An', '0901111222', 'Bạc', 'An Giang'),
('C002','Trần Văn Bình', '0912222333', 'Bạc', 'Cần Thơ'),
('C003','Phạm Văn Cường', '0987654321', 'VIP', 'Đồng Tháp')
ON DUPLICATE KEY UPDATE ma_khach_hang=ma_khach_hang;


--- Dữ liệu Sản phẩm ---
INSERT INTO `SanPham` (`ma_san_pham`, `ten_san_pham`, `don_vi_tinh`, `gia_ban`, `so_luong_ton`, `trang_thai`, `ma_nhan_vien_quan_ly`)
VALUES
('LAPTOP-001', 'Laptop Dell XPS 13', 'Chiếc', 25000000, 15, 'Đang bán', 'NV001'),
('PHONE-005', 'Điện thoại Samsung S24', 'Cái', 18000000, 50, 'Đang bán', 'NV002'),
('ACC-101', 'Chuột không dây Logitech', 'Cái', 450000, 150, 'Đang bán', 'NV001'),
('MONITOR-27', 'Màn hình Dell 27 inch', 'Cái', 6500000, 5, 'Hết hàng', NULL) 
ON DUPLICATE KEY UPDATE ma_san_pham=ma_san_pham;

--- Dữ liệu Hóa đơn ---
INSERT INTO `HoaDon` (`id_hoa_don`,`ma_khach_hang`, `ma_nhan_vien`,`ma_san_pham`,`ten_san_pham`, `tong_tien_phai_tra`, `tien_khach_thanh_toan`, `phuong_thuc_thanh_toan`, `trang_thai_thanh_toan`, `ngay_lap_hoa_don`)
VALUES
(1,'C001', 'NV002','LAPTOP-001','Laptop Dell XPS 13', 25000000, 25450000, 'Thẻ', 'Đã thanh toán', '2025-11-10 10:30:00'),
(2,'C002', 'NV002','PHONE-005', 'Điện thoại Samsung S24', 18000000, 18450000, 'Chuyển khoản', 'Đã thanh toán', '2025-11-11 14:00:00'),
(3,'C003', 'NV001','ACC-101', 'Chuột không dây Logitech', 450000, 500000, 'Tiền mặt', 'Đã thanh toán', '2025-11-12 11:00:00'),
(4,'C001', 'NV002','PHONE-005', 'Điện thoại Samsung S24', 18000000, 18000000, 'Thẻ', 'Đã thanh toán', '2025-11-14 16:00:00'),
(5,'C003', 'NV003','MONITOR-27', 'Màn hình Dell 27 inch', 6500000, 6500000, 'Chuyển khoản', 'Đã hủy', '2025-11-15 09:00:00') 
ON DUPLICATE KEY UPDATE id_hoa_don=id_hoa_don;
