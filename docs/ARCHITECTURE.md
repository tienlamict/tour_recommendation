# System Architecture - Tour Recommendation System

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         USER                                 │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    GUI LAYER (Tkinter)                       │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Comparison   │  │  TOPSIS      │  │   Results    │      │
│  │     Tab      │  │ Weights Tab  │  │     Tab      │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│                                                               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │         Components (Matrix, Loading, etc.)           │   │
│  └──────────────────────────────────────────────────────┘   │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                   SERVICE LAYER                              │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────────────┐  ┌──────────────────────┐         │
│  │   Tour Service       │  │ Recommendation       │         │
│  │   - CRUD Tours       │  │    Service           │         │
│  │   - Get Criteria     │  │ - Calculate AHP      │         │
│  │   - Filter           │  │ - Calculate TOPSIS   │         │
│  │   - Preferences      │  │ - Rank Tours         │         │
│  └──────────────────────┘  └──────────────────────┘         │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                  ALGORITHM LAYER                             │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │     AHP      │  │   TOPSIS     │  │  Validator   │      │
│  │  Calculator  │  │  Calculator  │  │   (CR)       │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    MODEL LAYER                               │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │     Tour     │  │  Criterion   │  │   Preference │      │
│  │    Model     │  │    Model     │  │    Model     │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                  DATABASE LAYER                              │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────────────────────────────────────────────┐   │
│  │         Connection Pool (MySQL Connector)            │   │
│  │         - Retry Logic                                │   │
│  │         - Health Check                               │   │
│  └──────────────────────────────────────────────────────┘   │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                   DATABASE (MySQL 8.0)                       │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │  tours   │  │ criteria │  │tour_crit │  │user_pref │   │
│  │  (15)    │  │   (6)    │  │  (90)    │  │   (n)    │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## Data Flow

### 1. User Input Flow (AHP)

```
User Input (Tab 1)
    │
    ├─► Matrix Input Widget
    │       │
    │       ├─► Validate Saaty Scale (1/9 to 9)
    │       ├─► Auto-calculate Reciprocals
    │       └─► Build Comparison Matrix (6×6)
    │
    ├─► AHP Calculator
    │       │
    │       ├─► Calculate Weights (Geometric Mean)
    │       └─► Return: weights[6]
    │
    └─► Consistency Validator
            │
            ├─► Calculate λmax
            ├─► Calculate CI = (λmax - n) / (n - 1)
            ├─► Calculate CR = CI / RI
            └─► Return: CR value
```

### 2. Recommendation Flow

```
Calculate Button Pressed
    │
    ├─► Validate Inputs
    │       ├─► Check criteria weights exist
    │       ├─► Check CR < 0.1
    │       └─► Check TOPSIS weights sum = 1.0
    │
    ├─► Load Tours from Database
    │       │
    │       └─► TourService.get_all_tours()
    │               │
    │               └─► Returns: List[Tour] with criterion scores
    │
    ├─► Calculate AHP Scores
    │       │
    │       ├─► For each tour:
    │       │       score = Σ(criteria_weight[i] × tour_criterion_score[i])
    │       │
    │       └─► Returns: tours with ahp_score populated
    │
    ├─► Calculate TOPSIS Scores
    │       │
    │       ├─► Build Decision Matrix [AHP, Price, Duration]
    │       ├─► Normalize Matrix
    │       ├─► Apply Weights
    │       ├─► Find Ideal Solutions (Positive & Negative)
    │       ├─► Calculate Distances (Euclidean)
    │       ├─► Calculate Scores: S- / (S+ + S-)
    │       │
    │       └─► Returns: tours with topsis_score populated
    │
    ├─► Rank Tours
    │       │
    │       └─► Sort by topsis_score (descending)
    │
    └─► Display Results (Tab 3)
            │
            └─► Show in TreeView
```

### 3. Export Flow

```
Export Button Pressed
    │
    ├─► CSV Export
    │       │
    │       ├─► Open File Dialog
    │       ├─► Build CSV Data
    │       │       ├─► Headers
    │       │       └─► Tour rows
    │       └─► Write to File (UTF-8 with BOM)
    │
    └─► PDF Export
            │
            ├─► Open File Dialog
            ├─► Build PDF Document
            │       ├─► Title & Metadata
            │       ├─► Summary Statistics
            │       ├─► Results Table
            │       └─► Top 5 Details
            └─► Generate PDF (ReportLab)
```

## Component Interaction Diagram

```
┌─────────────┐
│ MainWindow  │
└──────┬──────┘
       │
       ├──────────────┬──────────────┬──────────────┐
       │              │              │              │
       ▼              ▼              ▼              ▼
┌─────────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐
│Comparison   │ │ Weights  │ │ Results  │ │  Menu    │
│    Tab      │ │   Tab    │ │   Tab    │ │   Bar    │
└──────┬──────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘
       │             │            │            │
       │             │            │            │
       ▼             ▼            ▼            ▼
┌─────────────────────────────────────────────────┐
│         RecommendationService                   │
│  ┌──────────────┐      ┌──────────────┐        │
│  │ AHP          │      │ TOPSIS       │        │
│  │ Calculator   │◄─────┤ Calculator   │        │
│  └──────────────┘      └──────────────┘        │
└────────────┬────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────┐
│              TourService                         │
│  ┌──────────────────────────────────────┐       │
│  │      DatabaseConnection              │       │
│  │      (Connection Pool)               │       │
│  └──────────────┬───────────────────────┘       │
└─────────────────┼───────────────────────────────┘
                  │
                  ▼
           ┌──────────────┐
           │    MySQL     │
           │   Database   │
           └──────────────┘
```

## Algorithm Flow

### AHP Algorithm

```
Input: Comparison Matrix (n×n)
│
├─► Step 1: Validate Matrix
│       ├─► Check square matrix
│       ├─► Check diagonal = 1
│       ├─► Check reciprocal: a[i][j] = 1/a[j][i]
│       └─► Check positive values
│
├─► Step 2: Calculate Weights (Geometric Mean)
│       │
│       ├─► For each row i:
│       │       geometric_mean[i] = (∏ a[i][j])^(1/n)
│       │
│       └─► Normalize:
│               weight[i] = geometric_mean[i] / Σ geometric_mean
│
├─► Step 3: Calculate λmax
│       │
│       └─► λmax = (1/n) Σ (A·w)[i] / w[i]
│
├─► Step 4: Calculate CI
│       │
│       └─► CI = (λmax - n) / (n - 1)
│
├─► Step 5: Calculate CR
│       │
│       └─► CR = CI / RI[n]
│
└─► Output: weights, CR
```

### TOPSIS Algorithm

```
Input: Decision Matrix (m×n), Weights (n), Benefit Criteria (n)
│
├─► Step 1: Normalize Matrix
│       │
│       ├─► For benefit criteria:
│       │       r[i][j] = x[i][j] / √(Σ x[k][j]²)
│       │
│       └─► For cost criteria:
│               Invert: x'[i][j] = max(x[:,j]) - x[i][j]
│               Then normalize
│
├─► Step 2: Apply Weights
│       │
│       └─► v[i][j] = w[j] × r[i][j]
│
├─► Step 3: Find Ideal Solutions
│       │
│       ├─► Ideal Positive: v+[j] = max(v[:,j])
│       └─► Ideal Negative: v-[j] = min(v[:,j])
│
├─► Step 4: Calculate Distances
│       │
│       ├─► S+[i] = √(Σ (v[i][j] - v+[j])²)
│       └─► S-[i] = √(Σ (v[i][j] - v-[j])²)
│
├─► Step 5: Calculate Scores
│       │
│       └─► C[i] = S-[i] / (S+[i] + S-[i])
│
└─► Output: Scores (0 to 1), Ranked List
```

## Database Schema

```
┌─────────────────────────────────────────────┐
│                  tours                       │
├─────────────────────────────────────────────┤
│ PK  id (INT)                                │
│     name (VARCHAR)                          │
│     destination (VARCHAR)                   │
│     duration (INT)                          │
│     price (DECIMAL)                         │
│     max_participants (INT)                  │
│     difficulty_level (ENUM)                 │
│     season (VARCHAR)                        │
│     description (TEXT)                      │
│     image_url (VARCHAR)                     │
│     created_at (TIMESTAMP)                  │
│     updated_at (TIMESTAMP)                  │
└──────────┬──────────────────────────────────┘
           │
           │ 1:N
           │
           ▼
┌─────────────────────────────────────────────┐
│             tour_criteria                    │
├─────────────────────────────────────────────┤
│ PK  tour_id (INT) ──────────────┐           │
│ PK  criterion_id (INT)          │           │
│     score (DECIMAL)              │           │
└──────────┬───────────────────────┼───────────┘
           │                       │
           │ N:1                   │
           │                       │
           ▼                       │
┌─────────────────────────────────┼───────────┐
│              criteria            │           │
├──────────────────────────────────┘           │
│ PK  id (INT) ◄─────────────────────────────┘
│     name (VARCHAR)                          │
│     description (TEXT)                      │
│     icon (VARCHAR)                          │
│     created_at (TIMESTAMP)                  │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│           user_preferences                   │
├─────────────────────────────────────────────┤
│ PK  id (INT)                                │
│     user_name (VARCHAR)                     │
│     preference_data (JSON)                  │
│     created_at (TIMESTAMP)                  │
└─────────────────────────────────────────────┘
```

## Technology Stack

```
┌─────────────────────────────────────────────┐
│              Frontend (GUI)                  │
│  - Tkinter (Built-in)                       │
│  - ttk (Modern widgets)                     │
└─────────────────┬───────────────────────────┘
                  │
┌─────────────────▼───────────────────────────┐
│             Backend (Python)                 │
│  - Python 3.9+                              │
│  - numpy (Matrix operations)                │
│  - mysql-connector-python                   │
│  - python-dotenv                            │
│  - reportlab (PDF)                          │
└─────────────────┬───────────────────────────┘
                  │
┌─────────────────▼───────────────────────────┐
│            Database (MySQL)                  │
│  - MySQL 8.0                                │
│  - Docker Container                         │
│  - Connection Pooling                       │
└─────────────────────────────────────────────┘
```

## Deployment Architecture

```
┌─────────────────────────────────────────────┐
│          User's Computer                     │
│                                              │
│  ┌────────────────────────────────────┐     │
│  │   Python Application (run.py)      │     │
│  │   - GUI (Tkinter)                  │     │
│  │   - Business Logic                 │     │
│  │   - Algorithms                     │     │
│  └────────────┬───────────────────────┘     │
│               │                              │
│               │ TCP/IP (localhost:3306)      │
│               │                              │
│  ┌────────────▼───────────────────────┐     │
│  │   Docker Container                 │     │
│  │   ┌──────────────────────────┐     │     │
│  │   │   MySQL 8.0              │     │     │
│  │   │   - tours table          │     │     │
│  │   │   - criteria table       │     │     │
│  │   │   - tour_criteria table  │     │     │
│  │   │   - user_preferences     │     │     │
│  │   └──────────────────────────┘     │     │
│  └────────────────────────────────────┘     │
│                                              │
└─────────────────────────────────────────────┘
```

## Security Considerations

```
┌─────────────────────────────────────────────┐
│           Security Measures                  │
├─────────────────────────────────────────────┤
│  ✓ Environment Variables (.env)             │
│  ✓ No Hardcoded Passwords                   │
│  ✓ Parameterized SQL Queries                │
│  ✓ Input Validation                         │
│  ✓ Error Handling (No sensitive info)       │
│  ✓ Connection Pooling (Resource mgmt)       │
│  ✓ Docker Isolation                         │
└─────────────────────────────────────────────┘
```

## Performance Optimization

```
┌─────────────────────────────────────────────┐
│        Performance Features                  │
├─────────────────────────────────────────────┤
│  ✓ Connection Pooling                       │
│  ✓ Efficient Algorithms (O(n²) for AHP)     │
│  ✓ NumPy Vectorization                      │
│  ✓ Database Indexes                         │
│  ✓ Lazy Loading                             │
│  ✓ Caching (Matrix calculations)            │
└─────────────────────────────────────────────┘
```

## Scalability

```
Current: Single User, Local Database
    │
    ├─► Future: Multi-User
    │       ├─► Add User Authentication
    │       ├─► Session Management
    │       └─► User-specific Preferences
    │
    ├─► Future: Web Version
    │       ├─► Flask/FastAPI Backend
    │       ├─► React Frontend
    │       └─► RESTful API
    │
    └─► Future: Cloud Deployment
            ├─► AWS/Azure/GCP
            ├─► Managed Database
            └─► Load Balancing
```

---

This architecture provides:
- ✅ **Separation of Concerns**: Clear layer boundaries
- ✅ **Maintainability**: Easy to modify and extend
- ✅ **Testability**: Each component can be tested independently
- ✅ **Scalability**: Can be extended to web/cloud
- ✅ **Security**: Best practices implemented
- ✅ **Performance**: Optimized for efficiency

