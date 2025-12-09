"""Script to check database connection and data."""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config.database import DatabaseConnection, execute_query
from src.config.settings import Settings


def main():
    """Check database connection and data."""
    print("=" * 60)
    print("Database Connection Check")
    print("=" * 60)
    
    # Print configuration
    print("\nConfiguration:")
    print(f"  Host: {Settings.DB_HOST}")
    print(f"  Port: {Settings.DB_PORT}")
    print(f"  User: {Settings.DB_USER}")
    print(f"  Database: {Settings.DB_NAME}")
    
    # Test connection
    print("\nTesting connection...")
    try:
        DatabaseConnection.initialize_pool()
        
        if DatabaseConnection.test_connection():
            print("✓ Connection successful!")
        else:
            print("✗ Connection failed!")
            return
    except Exception as e:
        print(f"✗ Connection error: {e}")
        return
    
    # Check tables
    print("\nChecking tables...")
    try:
        # Count criteria
        result = execute_query("SELECT COUNT(*) as count FROM criteria")
        criteria_count = result[0]['count']
        print(f"  Criteria: {criteria_count} records")
        
        # Count tours
        result = execute_query("SELECT COUNT(*) as count FROM tours")
        tours_count = result[0]['count']
        print(f"  Tours: {tours_count} records")
        
        # Count tour_criteria
        result = execute_query("SELECT COUNT(*) as count FROM tour_criteria")
        tour_criteria_count = result[0]['count']
        print(f"  Tour-Criteria mappings: {tour_criteria_count} records")
        
        # Count user_preferences
        result = execute_query("SELECT COUNT(*) as count FROM user_preferences")
        preferences_count = result[0]['count']
        print(f"  User preferences: {preferences_count} records")
        
        print("\n✓ Database is ready!")
        
        # Show sample tours
        print("\nSample tours:")
        tours = execute_query("SELECT name, destination, price FROM tours LIMIT 5")
        for i, tour in enumerate(tours, 1):
            print(f"  {i}. {tour['name']} - {tour['destination']} ({tour['price']:,.0f} VNĐ)")
    
    except Exception as e:
        print(f"✗ Error checking tables: {e}")
        print("\nMake sure the database is initialized properly.")
        print("Try: cd docker && docker-compose down -v && docker-compose up -d")
    
    finally:
        DatabaseConnection.close_pool()
    
    print("\n" + "=" * 60)


if __name__ == '__main__':
    main()

