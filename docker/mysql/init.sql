-- Create database if not exists
CREATE DATABASE IF NOT EXISTS tour_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE tour_db;

-- Table: tours
CREATE TABLE IF NOT EXISTS tours (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    destination VARCHAR(200) NOT NULL,
    duration INT NOT NULL COMMENT 'Số ngày',
    price DECIMAL(12,2) NOT NULL COMMENT 'Giá VNĐ',
    max_participants INT NOT NULL,
    difficulty_level ENUM('easy', 'moderate', 'hard') DEFAULT 'moderate',
    season VARCHAR(100) COMMENT 'Mùa phù hợp',
    description TEXT,
    image_url VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_destination (destination),
    INDEX idx_price (price)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table: criteria
CREATE TABLE IF NOT EXISTS criteria (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    icon VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table: tour_criteria
CREATE TABLE IF NOT EXISTS tour_criteria (
    tour_id INT,
    criterion_id INT,
    score DECIMAL(3,2) NOT NULL COMMENT 'Điểm từ 0-10',
    FOREIGN KEY (tour_id) REFERENCES tours(id) ON DELETE CASCADE,
    FOREIGN KEY (criterion_id) REFERENCES criteria(id) ON DELETE CASCADE,
    PRIMARY KEY (tour_id, criterion_id),
    CHECK (score >= 0 AND score <= 10)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table: user_preferences
CREATE TABLE IF NOT EXISTS user_preferences (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_name VARCHAR(100),
    preference_data JSON COMMENT 'Ma trận so sánh và trọng số',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Insert criteria data
INSERT INTO criteria (name, description, icon) VALUES
('Phong cảnh', 'Cảnh đẹp, thiên nhiên', '🏞️'),
('Văn hóa', 'Di tích, lịch sử, văn hóa địa phương', '🏛️'),
('Ẩm thực', 'Đặc sản, món ăn địa phương', '🍜'),
('Mạo hiểm', 'Hoạt động mạo hiểm, thể thao', '🧗'),
('Thư giãn', 'Nghỉ dưỡng, spa, yên tĩnh', '🧘'),
('Mua sắm', 'Chợ, trung tâm thương mại', '🛍️');

-- Insert tour data
INSERT INTO tours (name, destination, duration, price, max_participants, difficulty_level, season, description) VALUES
('Hạ Long - Cát Bà', 'Quảng Ninh', 3, 4500000, 30, 'easy', 'Quanh năm', 'Khám phá vịnh Hạ Long - di sản thiên nhiên thế giới'),
('Sapa - Fansipan', 'Lào Cai', 4, 5200000, 25, 'hard', 'Tháng 9-11, 3-5', 'Chinh phục nóc nhà Đông Dương'),
('Phú Quốc nghỉ dưỡng', 'Kiên Giang', 5, 8000000, 40, 'easy', 'Tháng 11-4', 'Nghỉ dưỡng tại đảo ngọc Phú Quốc'),
('Đà Nẵng - Hội An', 'Đà Nẵng', 4, 6000000, 35, 'easy', 'Quanh năm', 'Khám phá phố cổ Hội An và biển Đà Nẵng'),
('Nha Trang biển', 'Khánh Hòa', 4, 5500000, 40, 'easy', 'Tháng 1-8', 'Tắm biển và vui chơi tại Nha Trang'),
('Đà Lạt lãng mạn', 'Lâm Đồng', 3, 3800000, 30, 'easy', 'Quanh năm', 'Thành phố ngàn hoa với khí hậu mát mẻ'),
('Mũi Né - Phan Thiết', 'Bình Thuận', 3, 3500000, 35, 'easy', 'Quanh năm', 'Đồi cát bay và biển đẹp'),
('Huế - Động Phong Nha', 'Thừa Thiên Huế', 4, 5800000, 30, 'moderate', 'Tháng 2-8', 'Di sản văn hóa và hang động kỳ vĩ'),
('Tây Bắc - Mù Cang Chải', 'Yên Bái', 5, 6500000, 20, 'moderate', 'Tháng 9-10', 'Ruộng bậc thang mùa lúa chín'),
('Côn Đảo', 'Bà Rịa - Vũng Tàu', 4, 9000000, 25, 'easy', 'Tháng 3-9', 'Đảo thiên đường với biển xanh ngắt'),
('Ninh Bình - Tràng An', 'Ninh Bình', 2, 2500000, 40, 'easy', 'Quanh năm', 'Vịnh Hạ Long trên cạn'),
('Cần Thơ - Miệt vườn', 'Cần Thơ', 3, 3200000, 35, 'easy', 'Quanh năm', 'Khám phá miệt vườn sông nước'),
('Quy Nhơn biển', 'Bình Định', 4, 4800000, 30, 'easy', 'Tháng 3-9', 'Bãi biển hoang sơ, yên bình'),
('Mai Châu - Pù Luông', 'Hòa Bình', 3, 3600000, 25, 'moderate', 'Quanh năm', 'Bản làng dân tộc và thiên nhiên'),
('Vũng Tàu cuối tuần', 'Bà Rịa - Vũng Tàu', 2, 2000000, 40, 'easy', 'Quanh năm', 'Nghỉ dưỡng cuối tuần gần Sài Gòn');

-- Insert tour_criteria scores (tour_id, criterion_id, score)
-- Tour 1: Hạ Long - Cát Bà (Phong cảnh cao, văn hóa trung bình, ẩm thực tốt)
INSERT INTO tour_criteria (tour_id, criterion_id, score) VALUES
(1, 1, 9.5), (1, 2, 7.0), (1, 3, 8.0), (1, 4, 6.5), (1, 5, 7.5), (1, 6, 6.0),
-- Tour 2: Sapa - Fansipan (Phong cảnh cao, mạo hiểm cao)
(2, 1, 9.8), (2, 2, 8.5), (2, 3, 7.5), (2, 4, 9.0), (2, 5, 5.0), (2, 6, 5.5),
-- Tour 3: Phú Quốc (Thư giãn cao, phong cảnh đẹp)
(3, 1, 9.0), (3, 2, 6.0), (3, 3, 8.5), (3, 4, 7.0), (3, 5, 9.5), (3, 6, 7.5),
-- Tour 4: Đà Nẵng - Hội An (Văn hóa cao, cân bằng)
(4, 1, 8.5), (4, 2, 9.5), (4, 3, 9.0), (4, 4, 6.0), (4, 5, 7.0), (4, 6, 8.0),
-- Tour 5: Nha Trang (Mạo hiểm, thư giãn)
(5, 1, 8.0), (5, 2, 6.5), (5, 3, 8.0), (5, 4, 8.5), (5, 5, 8.0), (5, 6, 7.0),
-- Tour 6: Đà Lạt (Phong cảnh, thư giãn, mua sắm)
(6, 1, 9.0), (6, 2, 7.0), (6, 3, 7.5), (6, 4, 5.0), (6, 5, 8.5), (6, 6, 8.5),
-- Tour 7: Mũi Né (Phong cảnh, thư giãn)
(7, 1, 8.5), (7, 2, 5.5), (7, 3, 7.0), (7, 4, 7.5), (7, 5, 8.0), (7, 6, 6.0),
-- Tour 8: Huế - Phong Nha (Văn hóa cao, mạo hiểm)
(8, 1, 9.0), (8, 2, 9.8), (8, 3, 8.5), (8, 4, 8.0), (8, 5, 6.0), (8, 6, 6.5),
-- Tour 9: Mù Cang Chải (Phong cảnh tuyệt đẹp, văn hóa)
(9, 1, 10.0), (9, 2, 8.0), (9, 3, 7.0), (9, 4, 7.0), (9, 5, 6.5), (9, 6, 5.0),
-- Tour 10: Côn Đảo (Phong cảnh, thư giãn, văn hóa)
(10, 1, 9.5), (10, 2, 8.0), (10, 3, 7.5), (10, 4, 7.5), (10, 5, 9.0), (10, 6, 6.0),
-- Tour 11: Ninh Bình (Phong cảnh, văn hóa)
(11, 1, 9.5), (11, 2, 8.5), (11, 3, 7.5), (11, 4, 6.0), (11, 5, 7.0), (11, 6, 6.5),
-- Tour 12: Cần Thơ (Văn hóa, ẩm thực)
(12, 1, 7.5), (12, 2, 8.0), (12, 3, 9.5), (12, 4, 5.0), (12, 5, 7.5), (12, 6, 7.5),
-- Tour 13: Quy Nhơn (Phong cảnh, thư giãn)
(13, 1, 8.5), (13, 2, 7.0), (13, 3, 8.0), (13, 4, 6.5), (13, 5, 8.5), (13, 6, 6.5),
-- Tour 14: Mai Châu - Pù Luông (Phong cảnh, văn hóa)
(14, 1, 9.0), (14, 2, 8.5), (14, 3, 7.5), (14, 4, 7.0), (14, 5, 7.5), (14, 6, 5.5),
-- Tour 15: Vũng Tàu (Thư giãn, mua sắm)
(15, 1, 7.0), (15, 2, 6.0), (15, 3, 7.5), (15, 4, 5.5), (15, 5, 8.0), (15, 6, 8.0);

