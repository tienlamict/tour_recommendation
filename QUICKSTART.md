# Quick Start Guide

## Bắt đầu nhanh trong 5 phút

### 1. Cài đặt Python packages

```bash
pip install -r requirements.txt
```

### 2. Khởi động Database

```bash
cd docker
docker-compose up -d
```

Đợi khoảng 10-20 giây để MySQL khởi động hoàn toàn.

### 3. Kiểm tra Database

```bash
docker-compose ps
```

Bạn sẽ thấy container `tour_db` đang chạy (status: Up).

### 4. Chạy ứng dụng

```bash
cd ..
python run.py
```

## Sử dụng nhanh

### Demo nhanh

1. **Tab 1 - So sánh tiêu chí**:
   - Nhấn nút "Ví dụ" để tải ma trận mẫu
   - Nhấn "Tính trọng số"
   - Kiểm tra CR < 0.1 ✓

2. **Tab 2 - Trọng số TOPSIS**:
   - Nhấn "Cân bằng" hoặc giữ nguyên mặc định
   - Đảm bảo tổng = 1.0

3. **Tính toán**:
   - Nhấn nút "Tính toán gợi ý Tour" ở dưới cùng
   - Xem kết quả trong Tab 3

4. **Xem chi tiết**:
   - Double-click vào tour bất kỳ để xem chi tiết
   - Nhấn "Xuất PDF" hoặc "Xuất CSV" để lưu kết quả

## Tùy chỉnh sở thích

### So sánh tiêu chí (Tab 1)

Ví dụ: Bạn thích phong cảnh hơn văn hóa

- Tìm ô (Phong cảnh, Văn hóa)
- Nhập số từ 1-9:
  - 1: Ngang nhau
  - 3: Phong cảnh quan trọng hơn một chút
  - 5: Phong cảnh quan trọng hơn
  - 7: Phong cảnh quan trọng hơn nhiều
  - 9: Phong cảnh cực kỳ quan trọng hơn

### Điều chỉnh TOPSIS (Tab 2)

- **Ưu tiên chất lượng**: Kéo slider "Điểm AHP" lên cao
- **Ưu tiên giá rẻ**: Kéo slider "Giá" lên cao
- **Ưu tiên thời gian ngắn**: Kéo slider "Thời gian" lên cao

Hoặc dùng các nút preset có sẵn.

## Lưu và tải preferences

### Lưu

1. File → Lưu preferences
2. Nhập tên (ví dụ: "du_lich_bien")
3. Nhấn OK

### Tải

1. File → Tải preferences
2. Chọn file JSON đã lưu
3. Preferences sẽ được khôi phục

## Dừng ứng dụng

1. Đóng cửa sổ GUI
2. Dừng database (nếu muốn):
   ```bash
   cd docker
   docker-compose down
   ```

## Troubleshooting

### Lỗi "Không thể kết nối database"

```bash
# Kiểm tra Docker đang chạy
docker ps

# Khởi động lại database
cd docker
docker-compose down
docker-compose up -d

# Đợi 10-20 giây rồi chạy lại
cd ..
python run.py
```

### Lỗi "Module not found"

```bash
# Cài lại dependencies
pip install -r requirements.txt
```

### Database không có dữ liệu

Database sẽ tự động khởi tạo với 15 tours mẫu khi lần đầu chạy.

Nếu cần reset database:

```bash
cd docker
docker-compose down -v  # Xóa volumes
docker-compose up -d    # Khởi động lại
```

## Tips

1. **Consistency Ratio (CR)**:
   - CR < 0.1: Tốt ✓
   - CR >= 0.1: Nên xem xét lại so sánh

2. **Trọng số TOPSIS**:
   - Tổng phải = 1.0
   - Điều chỉnh để phản ánh ưu tiên của bạn

3. **Kết quả**:
   - Tours được sắp xếp theo điểm TOPSIS (cao → thấp)
   - Điểm TOPSIS càng cao càng phù hợp với sở thích

4. **Xuất báo cáo**:
   - CSV: Đơn giản, mở bằng Excel
   - PDF: Đẹp, có chi tiết đầy đủ

## Ví dụ kịch bản

### Kịch bản 1: Thích phong cảnh và thư giãn

1. Tab 1: So sánh
   - Phong cảnh vs Văn hóa: 5 (Phong cảnh quan trọng hơn)
   - Phong cảnh vs Ẩm thực: 3
   - Thư giãn vs Mạo hiểm: 7 (Thư giãn quan trọng hơn nhiều)
   - ...

2. Tab 2: TOPSIS
   - Điểm AHP: 0.6
   - Giá: 0.2
   - Thời gian: 0.2

3. Kết quả: Phú Quốc, Côn Đảo, Nha Trang...

### Kịch bản 2: Ưu tiên giá rẻ

1. Tab 1: Nhấn "Ví dụ"

2. Tab 2: Nhấn "Ưu tiên giá rẻ"
   - Điểm AHP: 0.2
   - Giá: 0.6
   - Thời gian: 0.2

3. Kết quả: Vũng Tàu, Ninh Bình, Cần Thơ...

## Liên hệ

Nếu có vấn đề, vui lòng tạo issue trên GitHub hoặc liên hệ team.

