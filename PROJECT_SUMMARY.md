# Tour Recommendation System - Project Summary

## Tổng quan dự án

Hệ thống gợi ý tour du lịch thông minh sử dụng kết hợp hai phương pháp ra quyết định đa tiêu chí:
- **AHP (Analytic Hierarchy Process)**: Xác định trọng số tiêu chí dựa trên sở thích người dùng
- **TOPSIS (Technique for Order Preference by Similarity to Ideal Solution)**: Xếp hạng các tour dựa trên nhiều tiêu chí

## Cấu trúc dự án

```
tour_recommendation/
├── src/                          # Source code chính
│   ├── algorithms/               # Thuật toán AHP và TOPSIS
│   │   ├── ahp.py               # AHP implementation
│   │   ├── topsis.py            # TOPSIS implementation
│   │   └── validator.py         # Consistency validation
│   ├── config/                  # Configuration
│   │   ├── settings.py          # Settings từ .env
│   │   └── database.py          # Database connection pool
│   ├── models/                  # Data models
│   │   ├── tour.py              # Tour và Criterion models
│   │   └── preference.py        # UserPreference model
│   ├── services/                # Business logic
│   │   ├── tour_service.py      # Tour CRUD operations
│   │   └── recommendation_service.py  # Recommendation logic
│   ├── gui/                     # Tkinter GUI
│   │   ├── main_window.py       # Main window
│   │   ├── comparison_tab.py    # AHP comparison tab
│   │   ├── weights_tab.py       # TOPSIS weights tab
│   │   ├── results_tab.py       # Results display tab
│   │   └── components/          # Reusable components
│   │       ├── matrix_input.py  # Matrix input widget
│   │       └── loading_dialog.py # Loading dialog
│   ├── utils/                   # Utilities
│   │   ├── logger.py            # Logging setup
│   │   ├── helpers.py           # Helper functions
│   │   └── export.py            # CSV/PDF export
│   └── main.py                  # Entry point
├── docker/                      # Docker setup
│   ├── docker-compose.yml       # Docker compose config
│   └── mysql/                   # MySQL configuration
│       ├── Dockerfile
│       ├── init.sql             # Database initialization
│       └── my.cnf               # MySQL config
├── tests/                       # Unit tests
│   ├── test_ahp.py
│   ├── test_topsis.py
│   └── test_tour_service.py
├── scripts/                     # Utility scripts
│   └── check_db.py              # Database check script
├── data/                        # User data
│   └── saved_preferences/       # Saved user preferences
├── requirements.txt             # Python dependencies
├── run.py                       # Run script
├── README.md                    # Full documentation
├── QUICKSTART.md                # Quick start guide
└── .env                         # Environment variables
```

## Các thành phần chính

### 1. Algorithms (src/algorithms/)

#### AHP Calculator (`ahp.py`)
- **Geometric Mean Method**: Tính trọng số từ ma trận so sánh
- **Eigenvalue Method**: Phương pháp Saaty gốc
- **Weight Calculation**: Tính điểm cho alternatives
- **Example Matrix**: Tạo ma trận mẫu

#### TOPSIS Calculator (`topsis.py`)
- **Matrix Normalization**: Chuẩn hóa ma trận quyết định
- **Weight Application**: Nhân trọng số
- **Ideal Solutions**: Tìm ideal positive/negative
- **Distance Calculation**: Tính khoảng cách Euclidean
- **Score Calculation**: Tính điểm TOPSIS

#### Consistency Validator (`validator.py`)
- **Lambda Max**: Tính eigenvalue lớn nhất
- **CI Calculation**: Consistency Index
- **CR Calculation**: Consistency Ratio
- **Matrix Validation**: Kiểm tra tính hợp lệ

### 2. Database (docker/mysql/)

#### Schema
- **tours**: Thông tin tour (15 tours mẫu)
- **criteria**: 6 tiêu chí đánh giá
- **tour_criteria**: Điểm số tour theo tiêu chí
- **user_preferences**: Lưu preferences người dùng

#### Connection Pool
- Retry logic với 3 lần thử
- Connection pooling để tối ưu performance
- Health check

### 3. GUI (src/gui/)

#### Tab 1: Comparison Tab
- Ma trận 6x6 so sánh tiêu chí
- Hỗ trợ nhập phân số (1/3, 1/5, ...)
- Tooltip giải thích
- Real-time CR calculation
- Load example matrix

#### Tab 2: Weights Tab
- 3 sliders cho AHP, Price, Duration
- Auto-adjust để tổng = 1.0
- Preset buttons (Quality, Price, Balanced)
- Real-time validation

#### Tab 3: Results Tab
- Treeview hiển thị kết quả
- Double-click xem chi tiết
- Export CSV/PDF
- Sort by TOPSIS score

### 4. Services (src/services/)

#### Tour Service
- CRUD operations cho tours
- Get criteria
- Filter tours
- Save/load user preferences

#### Recommendation Service
- Calculate AHP scores
- Calculate TOPSIS scores
- Generate recommendations
- Explain recommendations
- Compare tours

### 5. Export (src/utils/export.py)

#### CSV Export
- Simple table format
- UTF-8 with BOM
- All tour details

#### PDF Export
- Professional report layout
- Summary statistics
- Detailed tour information
- Criteria scores
- ReportLab library

## Workflow

```
1. User Input (Tab 1)
   ↓
   So sánh cặp tiêu chí (6x6 matrix)
   ↓
2. AHP Calculation
   ↓
   Tính trọng số tiêu chí
   Kiểm tra CR < 0.1
   ↓
3. User Input (Tab 2)
   ↓
   Điều chỉnh trọng số TOPSIS
   (AHP, Price, Duration)
   ↓
4. Load Tours from Database
   ↓
5. Calculate AHP Scores
   ↓
   Điểm tour = Σ(trọng số tiêu chí × điểm tiêu chí)
   ↓
6. Calculate TOPSIS Scores
   ↓
   Decision Matrix: [AHP, Price, Duration]
   Normalize → Weight → Ideal Solutions → Distance → Score
   ↓
7. Rank Tours
   ↓
   Sort by TOPSIS score (descending)
   ↓
8. Display Results (Tab 3)
   ↓
   Show ranked tours
   Export CSV/PDF
```

## Công thức toán học

### AHP

**Trọng số (Geometric Mean)**:
```
w_i = (∏_{j=1}^n a_{ij})^{1/n} / Σ_k (∏_{j=1}^n a_{kj})^{1/n}
```

**Consistency Ratio**:
```
λ_max = (1/n) Σ_i (Aw)_i / w_i
CI = (λ_max - n) / (n - 1)
CR = CI / RI
```

### TOPSIS

**Normalization**:
```
r_{ij} = x_{ij} / √(Σ_k x_{kj}^2)
```

**Weighted Matrix**:
```
v_{ij} = w_j × r_{ij}
```

**Distance**:
```
S_i^+ = √(Σ_j (v_{ij} - v_j^+)^2)
S_i^- = √(Σ_j (v_{ij} - v_j^-)^2)
```

**Score**:
```
C_i = S_i^- / (S_i^+ + S_i^-)
```

## Tính năng nổi bật

### 1. Validation đầy đủ
- Kiểm tra ma trận reciprocal
- Consistency Ratio < 0.1
- Trọng số sum = 1.0
- Input validation

### 2. User Experience
- Intuitive GUI
- Real-time feedback
- Loading dialogs
- Tooltips
- Error messages rõ ràng

### 3. Flexibility
- Save/Load preferences
- Multiple export formats
- Filter tours
- Compare tours
- Preset configurations

### 4. Performance
- Connection pooling
- Caching
- Async operations
- Efficient algorithms

### 5. Code Quality
- Type hints
- Docstrings
- Logging
- Unit tests
- SOLID principles
- Separation of concerns

## Dependencies

### Core
- **numpy**: Matrix operations
- **mysql-connector-python**: Database
- **python-dotenv**: Environment variables

### GUI
- **tkinter**: Built-in GUI framework
- **ttk**: Modern widgets

### Export
- **reportlab**: PDF generation
- **csv**: CSV export (built-in)

### Optional
- **matplotlib**: Charts (future feature)
- **Pillow**: Image handling

## Testing

### Unit Tests
- `test_ahp.py`: AHP algorithm tests
- `test_topsis.py`: TOPSIS algorithm tests
- `test_tour_service.py`: Service layer tests

### Coverage
- Algorithm correctness
- Weight calculation
- Consistency validation
- Matrix operations
- Database operations (mocked)

## Deployment

### Development
```bash
python run.py
```

### Production
1. Setup MySQL server
2. Configure .env
3. Run with proper logging
4. Monitor performance

### Docker
```bash
cd docker
docker-compose up -d
```

## Future Enhancements

### Planned Features
1. **Web Version**: Flask/FastAPI + React
2. **User Authentication**: Login/Register
3. **Review System**: User reviews
4. **Recommendation History**: Track history
5. **Collaborative Filtering**: Similar users
6. **Mobile App**: React Native
7. **Multi-language**: Vietnamese/English
8. **Charts**: Visualization with matplotlib
9. **Advanced Filters**: More filter options
10. **Batch Processing**: Process multiple users

### Technical Improvements
1. Caching layer (Redis)
2. Async database operations
3. API endpoints (REST/GraphQL)
4. Real-time updates (WebSocket)
5. Performance monitoring
6. A/B testing framework

## Metrics

### Code Statistics
- **Total Files**: ~30 Python files
- **Lines of Code**: ~3500+ lines
- **Test Coverage**: Core algorithms covered
- **Documentation**: Comprehensive

### Database
- **Tables**: 4
- **Sample Data**: 15 tours, 6 criteria
- **Relationships**: Properly normalized

### Performance
- **Calculation Time**: < 1 second for 15 tours
- **Database Queries**: Optimized with indexes
- **Memory Usage**: Minimal

## Conclusion

Dự án Tour Recommendation System là một hệ thống hoàn chỉnh với:
- ✅ Thuật toán AHP và TOPSIS chính xác
- ✅ GUI thân thiện, dễ sử dụng
- ✅ Database được thiết kế tốt
- ✅ Code quality cao, maintainable
- ✅ Documentation đầy đủ
- ✅ Testing cơ bản
- ✅ Export functionality
- ✅ Error handling tốt

Hệ thống sẵn sàng để sử dụng và có thể mở rộng cho nhiều tính năng khác trong tương lai.

