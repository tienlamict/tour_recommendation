# Tour Recommendation System

Hệ thống gợi ý tour du lịch thông minh sử dụng kết hợp phương pháp AHP (Analytic Hierarchy Process) và TOPSIS (Technique for Order Preference by Similarity to Ideal Solution).

## Tính năng

- **So sánh tiêu chí AHP**: So sánh cặp các tiêu chí du lịch theo thang Saaty
- **Kiểm tra nhất quán**: Tính toán Consistency Ratio (CR) để đảm bảo so sánh hợp lý
- **Trọng số TOPSIS**: Điều chỉnh trọng số cho điểm AHP, giá và thời gian
- **Gợi ý thông minh**: Xếp hạng tours dựa trên sở thích cá nhân
- **Xuất báo cáo**: Xuất kết quả ra CSV và PDF
- **Lưu/Tải preferences**: Lưu sở thích để sử dụng lại

## Tiêu chí đánh giá

1. **Phong cảnh** 🏞️ - Cảnh đẹp, thiên nhiên
2. **Văn hóa** 🏛️ - Di tích, lịch sử, văn hóa địa phương
3. **Ẩm thực** 🍜 - Đặc sản, món ăn địa phương
4. **Mạo hiểm** 🧗 - Hoạt động mạo hiểm, thể thao
5. **Thư giãn** 🧘 - Nghỉ dưỡng, spa, yên tĩnh
6. **Mua sắm** 🛍️ - Chợ, trung tâm thương mại

## Yêu cầu hệ thống

- Python 3.9+
- MySQL 8.0
- Docker (để chạy database)

## Cài đặt

### 1. Clone repository

```bash
git clone <repository-url>
cd tour_recommendation
```

### 2. Tạo virtual environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. Cài đặt dependencies

```bash
pip install -r requirements.txt
```

### 4. Cấu hình môi trường

Tạo file `.env` từ `.env.example`:

```bash
cp .env.example .env
```

Chỉnh sửa file `.env` nếu cần:

```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=tour_user
DB_PASSWORD=tour_password
DB_NAME=tour_db
```

### 5. Khởi động database

```bash
cd docker
docker-compose up -d
```

Kiểm tra database đã chạy:

```bash
docker-compose ps
```

### 6. Chạy ứng dụng

```bash
python run.py
```

## Cấu trúc thư mục

```
tour_recommendation/
├── src/
│   ├── algorithms/          # AHP và TOPSIS
│   ├── config/              # Cấu hình
│   ├── gui/                 # Giao diện Tkinter
│   ├── models/              # Data models
│   ├── services/            # Business logic
│   └── utils/               # Utilities
├── docker/                  # Docker setup
├── tests/                   # Unit tests
├── data/                    # Dữ liệu người dùng
├── requirements.txt
├── run.py
└── README.md
```

## Hướng dẫn sử dụng

### Bước 1: So sánh tiêu chí

1. Mở tab "1. So sánh tiêu chí"
2. So sánh từng cặp tiêu chí theo thang Saaty (1-9):
   - 1: Ngang nhau
   - 3: Quan trọng hơn một chút
   - 5: Quan trọng hơn
   - 7: Quan trọng hơn nhiều
   - 9: Cực kỳ quan trọng hơn
3. Có thể dùng phân số: 1/3, 1/5, 1/7, 1/9
4. Nhấn "Tính trọng số"
5. Kiểm tra CR < 0.1 (nhất quán)

### Bước 2: Điều chỉnh trọng số TOPSIS

1. Mở tab "2. Trọng số TOPSIS"
2. Điều chỉnh trọng số cho:
   - Điểm AHP (chất lượng)
   - Giá (chi phí)
   - Thời gian (số ngày)
3. Tổng phải bằng 1.0
4. Có thể dùng preset: "Ưu tiên chất lượng", "Ưu tiên giá rẻ", v.v.

### Bước 3: Xem kết quả

1. Nhấn nút "Tính toán gợi ý Tour"
2. Xem kết quả trong tab "3. Kết quả"
3. Double-click vào tour để xem chi tiết
4. Xuất CSV hoặc PDF nếu cần

### Lưu/Tải preferences

- **Lưu**: File → Lưu preferences
- **Tải**: File → Tải preferences

## Thuật toán

### AHP (Analytic Hierarchy Process)

1. So sánh cặp tiêu chí
2. Tính trọng số bằng Geometric Mean
3. Kiểm tra Consistency Ratio (CR < 0.1)
4. Tính điểm cho mỗi tour theo tiêu chí

### TOPSIS

1. Chuẩn hóa ma trận quyết định
2. Nhân với trọng số
3. Xác định ideal positive/negative solutions
4. Tính khoảng cách Euclidean
5. Tính điểm TOPSIS = S- / (S+ + S-)
6. Xếp hạng giảm dần

## Testing

Chạy unit tests:

```bash
python -m unittest discover tests
```

Chạy test cụ thể:

```bash
python -m unittest tests.test_ahp
python -m unittest tests.test_topsis
```

## Troubleshooting

### Không kết nối được database

1. Kiểm tra Docker đang chạy:
   ```bash
   docker ps
   ```

2. Khởi động lại container:
   ```bash
   cd docker
   docker-compose down
   docker-compose up -d
   ```

3. Kiểm tra logs:
   ```bash
   docker-compose logs mysql
   ```

### Lỗi import module

Đảm bảo đã activate virtual environment và cài đặt dependencies:

```bash
pip install -r requirements.txt
```

## Công nghệ sử dụng

- **Backend**: Python 3.9+
- **Database**: MySQL 8.0
- **GUI**: Tkinter với ttk
- **Libraries**:
  - numpy: Tính toán ma trận
  - mysql-connector-python: Kết nối database
  - python-dotenv: Quản lý biến môi trường
  - reportlab: Xuất PDF
  - matplotlib: Biểu đồ (tùy chọn)

## Tác giả

Tour Recommendation Team

## License

MIT License

## Đóng góp

Mọi đóng góp đều được chào đón! Vui lòng tạo issue hoặc pull request.

