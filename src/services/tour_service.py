"""Tour service for database operations."""

import logging
from typing import List, Optional, Dict
from datetime import datetime

from ..config.database import execute_query
from ..models.tour import Tour, Criterion

logger = logging.getLogger(__name__)


class TourService:
    """Service for managing tours and criteria."""
    
    @staticmethod
    def get_all_criteria() -> List[Criterion]:
        """Get all criteria from database.
        
        Returns:
            List of Criterion objects
        """
        query = "SELECT * FROM criteria ORDER BY id"
        results = execute_query(query)
        
        criteria = [
            Criterion(
                id=row['id'],
                name=row['name'],
                description=row['description'],
                icon=row['icon'],
                created_at=row['created_at']
            )
            for row in results
        ]
        
        logger.info(f"Loaded {len(criteria)} criteria")
        return criteria
    
    @staticmethod
    def get_criterion_by_id(criterion_id: int) -> Optional[Criterion]:
        """Get criterion by ID.
        
        Args:
            criterion_id: Criterion ID
            
        Returns:
            Criterion object or None
        """
        query = "SELECT * FROM criteria WHERE id = %s"
        results = execute_query(query, (criterion_id,))
        
        if not results:
            return None
        
        row = results[0]
        return Criterion(
            id=row['id'],
            name=row['name'],
            description=row['description'],
            icon=row['icon'],
            created_at=row['created_at']
        )
    
    @staticmethod
    def get_all_tours() -> List[Tour]:
        """Get all tours from database.
        
        Returns:
            List of Tour objects
        """
        query = """
            SELECT t.*, 
                   GROUP_CONCAT(CONCAT(c.name, ':', tc.score) SEPARATOR '|') as scores
            FROM tours t
            LEFT JOIN tour_criteria tc ON t.id = tc.tour_id
            LEFT JOIN criteria c ON tc.criterion_id = c.id
            GROUP BY t.id
            ORDER BY t.name
        """
        results = execute_query(query)
        
        tours = []
        for row in results:
            tour = Tour(
                id=row['id'],
                name=row['name'],
                destination=row['destination'],
                duration=row['duration'],
                price=float(row['price']),
                max_participants=row['max_participants'],
                difficulty_level=row['difficulty_level'],
                season=row['season'],
                description=row['description'],
                image_url=row['image_url'],
                created_at=row['created_at'],
                updated_at=row['updated_at']
            )
            
            # Parse criterion scores
            if row['scores']:
                for score_str in row['scores'].split('|'):
                    criterion_name, score = score_str.split(':')
                    tour.set_criterion_score(criterion_name, float(score))
            
            tours.append(tour)
        
        logger.info(f"Loaded {len(tours)} tours")
        return tours
    
    @staticmethod
    def get_tour_by_id(tour_id: int) -> Optional[Tour]:
        """Get tour by ID.
        
        Args:
            tour_id: Tour ID
            
        Returns:
            Tour object or None
        """
        query = """
            SELECT t.*, 
                   GROUP_CONCAT(CONCAT(c.name, ':', tc.score) SEPARATOR '|') as scores
            FROM tours t
            LEFT JOIN tour_criteria tc ON t.id = tc.tour_id
            LEFT JOIN criteria c ON tc.criterion_id = c.id
            WHERE t.id = %s
            GROUP BY t.id
        """
        results = execute_query(query, (tour_id,))
        
        if not results:
            return None
        
        row = results[0]
        tour = Tour(
            id=row['id'],
            name=row['name'],
            destination=row['destination'],
            duration=row['duration'],
            price=float(row['price']),
            max_participants=row['max_participants'],
            difficulty_level=row['difficulty_level'],
            season=row['season'],
            description=row['description'],
            image_url=row['image_url'],
            created_at=row['created_at'],
            updated_at=row['updated_at']
        )
        
        # Parse criterion scores
        if row['scores']:
            for score_str in row['scores'].split('|'):
                criterion_name, score = score_str.split(':')
                tour.set_criterion_score(criterion_name, float(score))
        
        return tour
    
    @staticmethod
    def filter_tours(
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        min_duration: Optional[int] = None,
        max_duration: Optional[int] = None,
        destination: Optional[str] = None,
        difficulty_level: Optional[str] = None
    ) -> List[Tour]:
        """Filter tours by criteria.
        
        Args:
            min_price: Minimum price
            max_price: Maximum price
            min_duration: Minimum duration
            max_duration: Maximum duration
            destination: Destination name
            difficulty_level: Difficulty level
            
        Returns:
            Filtered list of tours
        """
        conditions = []
        params = []
        
        if min_price is not None:
            conditions.append("t.price >= %s")
            params.append(min_price)
        
        if max_price is not None:
            conditions.append("t.price <= %s")
            params.append(max_price)
        
        if min_duration is not None:
            conditions.append("t.duration >= %s")
            params.append(min_duration)
        
        if max_duration is not None:
            conditions.append("t.duration <= %s")
            params.append(max_duration)
        
        if destination:
            conditions.append("t.destination LIKE %s")
            params.append(f"%{destination}%")
        
        if difficulty_level:
            conditions.append("t.difficulty_level = %s")
            params.append(difficulty_level)
        
        where_clause = " AND ".join(conditions) if conditions else "1=1"
        
        query = f"""
            SELECT t.*, 
                   GROUP_CONCAT(CONCAT(c.name, ':', tc.score) SEPARATOR '|') as scores
            FROM tours t
            LEFT JOIN tour_criteria tc ON t.id = tc.tour_id
            LEFT JOIN criteria c ON tc.criterion_id = c.id
            WHERE {where_clause}
            GROUP BY t.id
            ORDER BY t.name
        """
        
        results = execute_query(query, tuple(params))
        
        tours = []
        for row in results:
            tour = Tour(
                id=row['id'],
                name=row['name'],
                destination=row['destination'],
                duration=row['duration'],
                price=float(row['price']),
                max_participants=row['max_participants'],
                difficulty_level=row['difficulty_level'],
                season=row['season'],
                description=row['description'],
                image_url=row['image_url'],
                created_at=row['created_at'],
                updated_at=row['updated_at']
            )
            
            # Parse criterion scores
            if row['scores']:
                for score_str in row['scores'].split('|'):
                    criterion_name, score = score_str.split(':')
                    tour.set_criterion_score(criterion_name, float(score))
            
            tours.append(tour)
        
        logger.info(f"Filtered to {len(tours)} tours")
        return tours
    
    @staticmethod
    def save_user_preference(user_name: str, preference_data: str) -> int:
        """Save user preference to database.
        
        Args:
            user_name: User name
            preference_data: JSON string of preference data
            
        Returns:
            ID of saved preference
        """
        query = """
            INSERT INTO user_preferences (user_name, preference_data)
            VALUES (%s, %s)
        """
        preference_id = execute_query(query, (user_name, preference_data), fetch=False)
        logger.info(f"Saved preference for user '{user_name}' with ID {preference_id}")
        return preference_id
    
    @staticmethod
    def get_user_preferences(user_name: Optional[str] = None) -> List[Dict]:
        """Get user preferences.
        
        Args:
            user_name: Optional user name filter
            
        Returns:
            List of preference dictionaries
        """
        if user_name:
            query = "SELECT * FROM user_preferences WHERE user_name = %s ORDER BY created_at DESC"
            results = execute_query(query, (user_name,))
        else:
            query = "SELECT * FROM user_preferences ORDER BY created_at DESC"
            results = execute_query(query)
        
        logger.info(f"Retrieved {len(results)} preferences")
        return results
    
    @staticmethod
    def delete_user_preference(preference_id: int) -> None:
        """Delete user preference.
        
        Args:
            preference_id: Preference ID
        """
        query = "DELETE FROM user_preferences WHERE id = %s"
        execute_query(query, (preference_id,), fetch=False)
        logger.info(f"Deleted preference ID {preference_id}")

