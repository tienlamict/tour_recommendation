"""Main entry point for the application."""

import sys
import logging
from pathlib import Path

from .config.settings import Settings
from .config.database import DatabaseConnection
from .utils.logger import setup_logger
from .gui.main_window import MainWindow


def main():
    """Main function."""
    # Setup directories
    Settings.ensure_directories()
    
    # Setup logging
    log_file = Settings.BASE_DIR / 'tour_recommendation.log'
    logger = setup_logger(
        name='tour_recommendation',
        level=Settings.LOG_LEVEL,
        log_file=log_file
    )
    
    logger.info("=" * 60)
    logger.info(f"Starting {Settings.APP_NAME}")
    logger.info("=" * 60)
    
    try:
        # Initialize database connection pool
        logger.info("Initializing database connection pool...")
        DatabaseConnection.initialize_pool()
        
        # Test connection
        if not DatabaseConnection.test_connection():
            logger.error("Database connection test failed!")
            print("\n" + "=" * 60)
            print("LỖI: Không thể kết nối database!")
            print("=" * 60)
            print("\nVui lòng kiểm tra:")
            print("1. Docker container đang chạy:")
            print("   cd docker && docker-compose up -d")
            print("\n2. Cấu hình trong file .env:")
            print("   DB_HOST=localhost")
            print("   DB_PORT=3306")
            print("   DB_USER=tour_user")
            print("   DB_PASSWORD=tour_password")
            print("   DB_NAME=tour_db")
            print("\n3. MySQL service đã khởi động")
            print("=" * 60 + "\n")
            sys.exit(1)
        
        logger.info("Database connection successful")
        
        # Create and run main window
        logger.info("Starting GUI...")
        app = MainWindow()
        app.run()
        
        logger.info("Application closed normally")
    
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
        sys.exit(0)
    
    except Exception as e:
        logger.exception(f"Fatal error: {e}")
        print(f"\nLỗi nghiêm trọng: {e}")
        sys.exit(1)
    
    finally:
        # Cleanup
        DatabaseConnection.close_pool()
        logger.info("Cleanup completed")


if __name__ == '__main__':
    main()

