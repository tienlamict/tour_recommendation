"""Database connection management."""

import time
import logging
from typing import Optional
import mysql.connector
from mysql.connector import Error, pooling
from .settings import Settings

logger = logging.getLogger(__name__)


class DatabaseConnection:
    """Database connection manager with connection pooling."""
    
    _pool: Optional[pooling.MySQLConnectionPool] = None
    
    @classmethod
    def initialize_pool(cls, pool_name: str = "tour_pool", pool_size: int = 5) -> None:
        """Initialize connection pool.
        
        Args:
            pool_name: Name of the connection pool
            pool_size: Number of connections in the pool
        """
        try:
            if cls._pool is None:
                config = Settings.get_database_config()
                cls._pool = pooling.MySQLConnectionPool(
                    pool_name=pool_name,
                    pool_size=pool_size,
                    pool_reset_session=True,
                    **config
                )
                logger.info(f"Database connection pool initialized with size {pool_size}")
        except Error as e:
            logger.error(f"Error initializing connection pool: {e}")
            raise
    
    @classmethod
    def get_connection(cls, max_retries: int = 3, delay: int = 2):
        """Get a connection from the pool with retry logic.
        
        Args:
            max_retries: Maximum number of retry attempts
            delay: Delay in seconds between retries
            
        Returns:
            Database connection
            
        Raises:
            ConnectionError: If unable to establish connection after retries
        """
        if cls._pool is None:
            cls.initialize_pool()
        
        for attempt in range(max_retries):
            try:
                connection = cls._pool.get_connection()
                logger.debug(f"Database connection acquired (attempt {attempt + 1})")
                return connection
            except Error as e:
                logger.warning(f"Connection attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    time.sleep(delay)
                else:
                    logger.error("Failed to connect to database after all retries")
                    raise ConnectionError(f"Không thể kết nối database: {e}")
    
    @classmethod
    def test_connection(cls) -> bool:
        """Test database connection.
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            conn = cls.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
            cursor.close()
            conn.close()
            logger.info("Database connection test successful")
            return True
        except Exception as e:
            logger.error(f"Database connection test failed: {e}")
            return False
    
    @classmethod
    def close_pool(cls) -> None:
        """Close all connections in the pool."""
        if cls._pool:
            # Note: mysql.connector pooling doesn't have explicit close_all method
            # Connections are closed when they go out of scope
            cls._pool = None
            logger.info("Database connection pool closed")


def execute_query(query: str, params: tuple = None, fetch: bool = True):
    """Execute a database query.
    
    Args:
        query: SQL query string
        params: Query parameters (for parameterized queries)
        fetch: Whether to fetch results
        
    Returns:
        Query results if fetch=True, otherwise None
    """
    conn = None
    cursor = None
    try:
        conn = DatabaseConnection.get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query, params or ())
        
        if fetch:
            results = cursor.fetchall()
            return results
        else:
            conn.commit()
            return cursor.lastrowid
    except Error as e:
        logger.error(f"Database query error: {e}")
        if conn:
            conn.rollback()
        raise
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def execute_many(query: str, data: list) -> None:
    """Execute multiple queries (batch insert/update).
    
    Args:
        query: SQL query string
        data: List of parameter tuples
    """
    conn = None
    cursor = None
    try:
        conn = DatabaseConnection.get_connection()
        cursor = conn.cursor()
        cursor.executemany(query, data)
        conn.commit()
        logger.info(f"Batch operation completed: {cursor.rowcount} rows affected")
    except Error as e:
        logger.error(f"Batch operation error: {e}")
        if conn:
            conn.rollback()
        raise
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

