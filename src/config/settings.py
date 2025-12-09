"""Application settings and configuration."""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Settings:
    """Application configuration settings."""
    
    # Database Configuration
    DB_HOST: str = os.getenv('DB_HOST', 'localhost')
    DB_PORT: int = int(os.getenv('DB_PORT', '3306'))
    DB_USER: str = os.getenv('DB_USER', 'tour_user')
    DB_PASSWORD: str = os.getenv('DB_PASSWORD', 'tour_password')
    DB_NAME: str = os.getenv('DB_NAME', 'tour_db')
    
    # Application Configuration
    APP_NAME: str = os.getenv('APP_NAME', 'Tour Recommendation System')
    LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')
    MAX_TOURS_DISPLAY: int = int(os.getenv('MAX_TOURS_DISPLAY', '20'))
    
    # AHP Configuration
    MAX_CR: float = 0.1  # Maximum Consistency Ratio
    SAATY_SCALE_MIN: float = 1/9
    SAATY_SCALE_MAX: float = 9
    
    # GUI Configuration
    WINDOW_WIDTH: int = 1200
    WINDOW_HEIGHT: int = 800
    
    # Paths
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
    DATA_DIR: Path = BASE_DIR / 'data'
    SAVED_PREFERENCES_DIR: Path = DATA_DIR / 'saved_preferences'
    
    @classmethod
    def ensure_directories(cls) -> None:
        """Ensure required directories exist."""
        cls.DATA_DIR.mkdir(exist_ok=True)
        cls.SAVED_PREFERENCES_DIR.mkdir(exist_ok=True)
    
    @classmethod
    def get_database_config(cls) -> dict:
        """Get database configuration as dictionary."""
        return {
            'host': cls.DB_HOST,
            'port': cls.DB_PORT,
            'user': cls.DB_USER,
            'password': cls.DB_PASSWORD,
            'database': cls.DB_NAME,
            'charset': 'utf8mb4',
            'collation': 'utf8mb4_unicode_ci'
        }

