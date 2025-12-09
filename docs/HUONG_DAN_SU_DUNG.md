# HƯỚNG DẪN SỬ DỤNG HỆ THỐNG GỢI Ý TOUR DU LỊCH

## MỤC LỤC

1. [Giới thiệu](#giới-thiệu)
2. [Cài đặt](#cài-đặt)
3. [Khởi động hệ thống](#khởi-động-hệ-thống)
4. [Hướng dẫn sử dụng](#hướng-dẫn-sử-dụng)
5. [Ví dụ thực tế](#ví-dụ-thực-tế)
6. [Giải thích thuật toán](#giải-thích-thuật-toán)
7. [Xử lý lỗi](#xử-lý-lỗi)
8. [FAQ](#faq)

---

## GIỚI THIỆU

### Hệ thống là gì?

Hệ thống gợi ý tour du lịch giúp bạn tìm tour phù hợp nhất dựa trên sở thích cá nhân về:
- 🏞️ **Phong cảnh**: Cảnh đẹp, thiên nhiên
- 🏛️ **Văn hóa**: Di tích, lịch sử
- 🍜 **Ẩm thực**: Đặc sản địa phương
- 🧗 **Mạo hiểm**: Hoạt động thể thao
- 🧘 **Thư giãn**: Nghỉ dưỡng, spa
- 🛍️ **Mua sắm**: Chợ, trung tâm thương mại

### Phương pháp sử dụng

Hệ thống kết hợp 2 phương pháp khoa học:

1. **AHP (Analytic Hierarchy Process)**:
   - Xác định mức độ quan trọng của từng tiêu chí
   - Dựa trên so sánh cặp (pairwise comparison)
   - Đảm bảo tính nhất quán (Consistency Ratio)

2. **TOPSIS (Technique for Order Preference by Similarity to Ideal Solution)**:
   - Xếp hạng các tour
   - Dựa trên khoảng cách đến giải pháp lý tưởng
   - Cân nhắc cả chất lượng, giá cả và thời gian

---

## CÀI ĐẶT

### Yêu cầu hệ thống

- **Python**: 3.9 trở lên
- **Docker**: Để chạy MySQL database
- **RAM**: Tối thiểu 4GB
- **Hệ điều hành**: Windows, Linux, hoặc macOS

### Bước 1: Cài đặt Python

#### Windows
1. Tải Python từ https://www.python.org/downloads/
2. Chạy installer, **QUAN TRỌNG**: Tick "Add Python to PATH"
3. Kiểm tra: Mở Command Prompt, gõ `python --version`

#### Linux/Mac
```bash
# Linux (Ubuntu/Debian)
sudo apt update
sudo apt install python3.9 python3-pip

# Mac (với Homebrew)
brew install python@3.9
```

### Bước 2: Cài đặt Docker

#### Windows/Mac
1. Tải Docker Desktop từ https://www.docker.com/products/docker-desktop
2. Cài đặt và khởi động Docker Desktop

#### Linux
```bash
sudo apt update
sudo apt install docker.io docker-compose
sudo systemctl start docker
sudo systemctl enable docker
```

### Bước 3: Clone hoặc tải project

```bash
# Nếu có Git
git clone <repository-url>
cd tour_recommendation

# Hoặc tải ZIP và giải nén
```

### Bước 4: Cài đặt Python packages

```bash
# Tạo virtual environment (khuyến nghị)
python -m venv venv

# Kích hoạt virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Cài đặt dependencies
pip install -r requirements.txt
```

### Bước 5: Cấu hình

File `.env` đã được tạo sẵn với cấu hình mặc định. Nếu cần thay đổi:

```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=tour_user
DB_PASSWORD=tour_password
DB_NAME=tour_db
```

---

## KHỞI ĐỘNG HỆ THỐNG

### 1. Khởi động Database

```bash
cd docker
docker-compose up -d
```

**Đợi 10-20 giây** để MySQL khởi động hoàn toàn.

Kiểm tra:
```bash
docker-compose ps
```

Bạn sẽ thấy:
```
NAME       IMAGE      STATUS
tour_db    mysql:8.0  Up
```

### 2. Kiểm tra Database (Tùy chọn)

```bash
cd ..
python scripts/check_db.py
```

Kết quả mong đợi:
```
✓ Connection successful!
  Criteria: 6 records
  Tours: 15 records
  Tour-Criteria mappings: 90 records
```

### 3. Chạy ứng dụng

```bash
python run.py
```

Cửa sổ GUI sẽ mở ra!

---

## HƯỚNG DẪN SỬ DỤNG

### Giao diện chính

Ứng dụng có 3 tabs chính:

```
┌─────────────────────────────────────────────┐
│ Tour Recommendation System                  │
├─────────────────────────────────────────────┤
│ [1. So sánh tiêu chí] [2. Trọng số TOPSIS] [3. Kết quả] │
├─────────────────────────────────────────────┤
│                                             │
│         (Nội dung tab)                      │
│                                             │
├─────────────────────────────────────────────┤
│              [Tính toán gợi ý Tour]         │
└─────────────────────────────────────────────┘
```

### Tab 1: So sánh tiêu chí

#### Mục đích
Xác định mức độ quan trọng của từng tiêu chí theo sở thích của bạn.

#### Cách sử dụng

1. **Hiểu thang đo Saaty (1-9)**:
   - **1**: Hai tiêu chí ngang nhau quan trọng
   - **3**: Tiêu chí này quan trọng hơn một chút
   - **5**: Tiêu chí này quan trọng hơn
   - **7**: Tiêu chí này quan trọng hơn nhiều
   - **9**: Tiêu chí này cực kỳ quan trọng hơn
   - **2, 4, 6, 8**: Các giá trị trung gian
   - **1/3, 1/5, 1/7, 1/9**: Khi tiêu chí thứ hai quan trọng hơn

2. **Nhập so sánh**:
   - Chỉ cần nhập nửa trên của ma trận (phần màu trắng)
   - Nửa dưới tự động tính (reciprocal)
   - Đường chéo luôn là 1

3. **Ví dụ**: Bạn thích phong cảnh hơn văn hóa
   - Tìm ô (Phong cảnh, Văn hóa)
   - Nhập: `5` (phong cảnh quan trọng hơn)
   - Ô (Văn hóa, Phong cảnh) tự động = `1/5`

4. **Tính trọng số**:
   - Nhấn nút **"Tính trọng số"**
   - Xem kết quả:
     - Trọng số từng tiêu chí (tổng = 1.0)
     - Consistency Ratio (CR)

5. **Kiểm tra nhất quán**:
   - **CR < 0.1**: ✓ Tốt, so sánh hợp lý
   - **CR >= 0.1**: ✗ Nên xem xét lại
   
   Nếu CR cao, có thể bạn đã:
   - So sánh không nhất quán (A > B, B > C, nhưng C > A)
   - Cần điều chỉnh một số giá trị

#### Các nút chức năng

- **Tính trọng số**: Tính toán trọng số tiêu chí
- **Kiểm tra nhất quán**: Chỉ kiểm tra CR, không tính toán
- **Ví dụ**: Tải ma trận mẫu để tham khảo
- **Xóa**: Xóa tất cả, reset về 1

### Tab 2: Trọng số TOPSIS

#### Mục đích
Điều chỉnh mức độ quan trọng của 3 yếu tố quyết định cuối cùng:
- Điểm AHP (chất lượng tour)
- Giá (chi phí)
- Thời gian (số ngày)

#### Cách sử dụng

1. **Kéo các slider**:
   - Mỗi slider từ 0.0 đến 1.0
   - Tổng phải = 1.0 (100%)
   - Tổng hiển thị real-time

2. **Ý nghĩa**:
   - **Điểm AHP cao**: Ưu tiên chất lượng, tour phù hợp sở thích
   - **Giá cao**: Ưu tiên tour giá rẻ
   - **Thời gian cao**: Ưu tiên tour ngắn ngày

3. **Preset nhanh**:
   - **Ưu tiên chất lượng**: AHP=0.7, Price=0.2, Duration=0.1
   - **Ưu tiên giá rẻ**: AHP=0.2, Price=0.6, Duration=0.2
   - **Ưu tiên thời gian ngắn**: AHP=0.2, Price=0.2, Duration=0.6
   - **Cân bằng**: AHP=0.5, Price=0.3, Duration=0.2

### Tab 3: Kết quả

#### Hiển thị

Bảng kết quả với các cột:
- **STT**: Thứ tự xếp hạng
- **Tên Tour**: Tên tour
- **Điểm đến**: Địa điểm
- **Số ngày**: Thời gian tour
- **Giá**: Giá tour (triệu VNĐ)
- **Điểm AHP**: Điểm chất lượng (0-1)
- **Điểm TOPSIS**: Điểm tổng hợp (0-1)

Tours được sắp xếp theo **Điểm TOPSIS giảm dần** (cao nhất ở trên).

#### Tương tác

1. **Xem chi tiết**:
   - Double-click vào tour
   - Popup hiển thị:
     - Thông tin cơ bản
     - Điểm theo từng tiêu chí
     - Mô tả chi tiết

2. **Xuất kết quả**:
   - **Xuất CSV**: File Excel đơn giản
   - **Xuất PDF**: Báo cáo đẹp, chi tiết

3. **Làm mới**: Refresh hiển thị

### Quy trình hoàn chỉnh

```
1. Tab 1: So sánh tiêu chí
   ↓
   Nhập ma trận so sánh
   ↓
   Nhấn "Tính trọng số"
   ↓
   Kiểm tra CR < 0.1
   ↓
2. Tab 2: Trọng số TOPSIS
   ↓
   Điều chỉnh sliders
   ↓
   Đảm bảo tổng = 1.0
   ↓
3. Nhấn "Tính toán gợi ý Tour"
   ↓
   Đợi vài giây
   ↓
4. Tab 3: Xem kết quả
   ↓
   Double-click xem chi tiết
   ↓
   Xuất CSV/PDF nếu cần
```

---

## VÍ DỤ THỰC TẾ

### Ví dụ 1: Du lịch nghỉ dưỡng

**Mục tiêu**: Tìm tour nghỉ dưỡng, thư giãn, phong cảnh đẹp

**Bước 1: So sánh tiêu chí**

| So sánh | Giá trị | Giải thích |
|---------|---------|------------|
| Phong cảnh vs Văn hóa | 5 | Phong cảnh quan trọng hơn |
| Phong cảnh vs Ẩm thực | 3 | Phong cảnh quan trọng hơn một chút |
| Phong cảnh vs Mạo hiểm | 7 | Phong cảnh quan trọng hơn nhiều |
| Phong cảnh vs Thư giãn | 1 | Ngang nhau |
| Phong cảnh vs Mua sắm | 9 | Phong cảnh cực kỳ quan trọng hơn |
| Thư giãn vs Mạo hiểm | 9 | Thư giãn cực kỳ quan trọng hơn |
| ... | ... | ... |

**Kết quả trọng số**:
- Phong cảnh: 35%
- Thư giãn: 30%
- Văn hóa: 15%
- Ẩm thực: 10%
- Mua sắm: 7%
- Mạo hiểm: 3%

**Bước 2: TOPSIS**
- Điểm AHP: 0.6 (ưu tiên chất lượng)
- Giá: 0.2
- Thời gian: 0.2

**Kết quả**:
1. Phú Quốc nghỉ dưỡng (TOPSIS: 0.87)
2. Côn Đảo (TOPSIS: 0.83)
3. Đà Lạt lãng mạn (TOPSIS: 0.79)

### Ví dụ 2: Du lịch văn hóa

**Mục tiêu**: Tìm hiểu văn hóa, lịch sử, ẩm thực

**Bước 1: So sánh tiêu chí**
- Văn hóa: 40%
- Ẩm thực: 25%
- Phong cảnh: 20%
- Thư giãn: 10%
- Mua sắm: 3%
- Mạo hiểm: 2%

**Bước 2: TOPSIS**
- Điểm AHP: 0.7
- Giá: 0.2
- Thời gian: 0.1

**Kết quả**:
1. Huế - Động Phong Nha (TOPSIS: 0.91)
2. Đà Nẵng - Hội An (TOPSIS: 0.88)
3. Ninh Bình - Tràng An (TOPSIS: 0.82)

### Ví dụ 3: Du lịch tiết kiệm

**Mục tiêu**: Tour giá rẻ, thời gian ngắn

**Bước 1: So sánh tiêu chí**
- Dùng preset "Ví dụ" hoặc cân bằng các tiêu chí

**Bước 2: TOPSIS**
- Nhấn "Ưu tiên giá rẻ"
- Điểm AHP: 0.2
- Giá: 0.6 (quan trọng nhất)
- Thời gian: 0.2

**Kết quả**:
1. Vũng Tàu cuối tuần (TOPSIS: 0.89)
2. Ninh Bình - Tràng An (TOPSIS: 0.85)
3. Cần Thơ - Miệt vườn (TOPSIS: 0.81)

---

## GIẢI THÍCH THUẬT TOÁN

### AHP - Tại sao phải so sánh cặp?

**Vấn đề**: Khó xác định trực tiếp mức độ quan trọng tuyệt đối của mỗi tiêu chí.

**Giải pháp**: So sánh từng cặp dễ hơn!
- "Phong cảnh có quan trọng hơn Văn hóa không?"
- "Quan trọng hơn bao nhiêu? (1-9)"

**Ưu điểm**:
- Dễ trả lời hơn
- Kết quả chính xác hơn
- Có thể kiểm tra tính nhất quán

### Consistency Ratio (CR)

**CR là gì?**
- Chỉ số đo mức độ nhất quán của so sánh
- CR = CI / RI
  - CI: Consistency Index (từ ma trận)
  - RI: Random Index (từ bảng chuẩn)

**Ý nghĩa**:
- **CR < 0.1**: Tốt ✓ (Saaty khuyến nghị)
- **CR >= 0.1**: Nên xem xét lại

**Ví dụ không nhất quán**:
- A quan trọng hơn B (5 lần)
- B quan trọng hơn C (5 lần)
- Nhưng A chỉ quan trọng hơn C (3 lần) ← Không hợp lý!
- Lẽ ra A phải quan trọng hơn C khoảng 25 lần (5×5)

### TOPSIS - Tại sao dùng khoảng cách?

**Ý tưởng**:
- Tour tốt nhất = Gần với "ideal positive" (tour lý tưởng)
- Tour tốt nhất = Xa với "ideal negative" (tour tệ nhất)

**Ideal Positive**: Tour có tất cả điểm tốt nhất
- AHP cao nhất
- Giá thấp nhất
- Thời gian ngắn nhất

**Ideal Negative**: Tour có tất cả điểm tệ nhất
- AHP thấp nhất
- Giá cao nhất
- Thời gian dài nhất

**Điểm TOPSIS**:
```
Score = Khoảng cách đến Negative / (Khoảng cách đến Positive + Khoảng cách đến Negative)
```

Điểm càng cao = Tour càng gần với lý tưởng!

---

## XỬ LÝ LỖI

### Lỗi 1: "Không thể kết nối database"

**Nguyên nhân**:
- Docker chưa chạy
- MySQL chưa khởi động xong
- Cấu hình sai

**Giải pháp**:

```bash
# 1. Kiểm tra Docker
docker ps

# 2. Khởi động lại database
cd docker
docker-compose down
docker-compose up -d

# 3. Đợi 20 giây
sleep 20

# 4. Kiểm tra
python scripts/check_db.py

# 5. Chạy lại app
cd ..
python run.py
```

### Lỗi 2: "Ma trận không nhất quán (CR >= 0.1)"

**Nguyên nhân**:
- So sánh không logic
- Mâu thuẫn giữa các so sánh

**Giải pháp**:
1. Xem lại các so sánh
2. Tìm mâu thuẫn (A>B, B>C, nhưng C>A)
3. Điều chỉnh giá trị
4. Tính lại

**Tips**: Nếu không chắc, dùng giá trị nhỏ hơn (1, 3, 5 thay vì 7, 9)

### Lỗi 3: "Tổng trọng số TOPSIS không bằng 1.0"

**Nguyên nhân**:
- Sliders chưa điều chỉnh đúng

**Giải pháp**:
1. Kéo các slider cho đến khi tổng = 1.000
2. Hoặc nhấn một trong các nút preset

### Lỗi 4: "Module not found"

**Nguyên nhân**:
- Chưa cài đặt dependencies
- Virtual environment chưa activate

**Giải pháp**:

```bash
# Activate venv
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Cài lại
pip install -r requirements.txt
```

### Lỗi 5: "Permission denied" (Docker)

**Nguyên nhân**: User không có quyền Docker

**Giải pháp** (Linux):

```bash
sudo usermod -aG docker $USER
# Logout và login lại
```

---

## FAQ

### Q1: Tôi nên chọn giá trị bao nhiêu khi so sánh?

**A**: Dựa vào cảm nhận của bạn:
- **1**: Ngang nhau
- **3**: Hơn một chút (slightly more)
- **5**: Hơn rõ rệt (strongly more)
- **7**: Hơn nhiều (very strongly more)
- **9**: Hơn cực kỳ nhiều (extremely more)

Không chắc? Dùng 1, 3, 5 là an toàn.

### Q2: CR của tôi là 0.12, có sao không?

**A**: Theo Saaty, nên < 0.1. Nhưng:
- 0.10 - 0.15: Chấp nhận được trong một số trường hợp
- > 0.15: Nên xem xét lại

### Q3: Tại sao kết quả khác với mong đợi?

**A**: Có thể do:
1. Trọng số TOPSIS chưa phù hợp
   - Thử điều chỉnh slider
   - Thử các preset khác nhau
2. So sánh tiêu chí chưa phản ánh đúng sở thích
   - Xem lại trọng số tiêu chí
   - Điều chỉnh ma trận so sánh

### Q4: Tôi có thể thêm tour mới không?

**A**: Hiện tại cần thêm trực tiếp vào database:

```sql
INSERT INTO tours (name, destination, duration, price, ...)
VALUES ('Tour mới', 'Địa điểm', 3, 5000000, ...);
```

Tính năng thêm qua GUI sẽ có trong phiên bản sau.

### Q5: Làm sao lưu preferences?

**A**:
1. File → Lưu preferences
2. Nhập tên (ví dụ: "du_lich_bien_2024")
3. File được lưu trong `data/saved_preferences/`
4. Có thể tải lại: File → Tải preferences

### Q6: Tôi có thể dùng hệ thống này cho mục đích khác không?

**A**: Có! Hệ thống AHP + TOPSIS có thể áp dụng cho:
- Chọn nhà đất
- Chọn trường học
- Chọn công việc
- Đánh giá nhà cung cấp
- Bất kỳ quyết định đa tiêu chí nào

Chỉ cần thay đổi:
- Tiêu chí (criteria)
- Alternatives (tours → houses, schools, ...)
- Điểm số

### Q7: Hệ thống có hỗ trợ tiếng Anh không?

**A**: Hiện tại chỉ tiếng Việt. Tính năng đa ngôn ngữ sẽ có trong tương lai.

### Q8: Tôi có thể chạy trên server không?

**A**: Có, nhưng cần:
1. Cài đặt X server (cho GUI) hoặc
2. Đợi phiên bản web (Flask/FastAPI)

---

## KẾT LUẬN

Hệ thống Tour Recommendation là công cụ mạnh mẽ giúp bạn:
- ✅ Tìm tour phù hợp với sở thích
- ✅ Ra quyết định dựa trên khoa học
- ✅ So sánh và đánh giá các lựa chọn
- ✅ Tiết kiệm thời gian tìm kiếm

**Chúc bạn tìm được tour ưng ý! 🎉**

---

## HỖ TRỢ

Nếu gặp vấn đề:
1. Xem phần [Xử lý lỗi](#xử-lý-lỗi)
2. Xem phần [FAQ](#faq)
3. Kiểm tra file log: `tour_recommendation.log`
4. Tạo issue trên GitHub

**Email**: support@tourrecommendation.com (nếu có)
**GitHub**: <repository-url>

