"""Tests for tour service."""

import unittest
from unittest.mock import Mock, patch
from src.services.tour_service import TourService
from src.models.tour import Tour, Criterion


class TestTourService(unittest.TestCase):
    """Test tour service."""
    
    @patch('src.services.tour_service.execute_query')
    def test_get_all_criteria(self, mock_execute):
        """Test getting all criteria."""
        # Mock database response
        mock_execute.return_value = [
            {
                'id': 1,
                'name': 'Phong cảnh',
                'description': 'Cảnh đẹp',
                'icon': '🏞️',
                'created_at': None
            },
            {
                'id': 2,
                'name': 'Văn hóa',
                'description': 'Di tích',
                'icon': '🏛️',
                'created_at': None
            }
        ]
        
        criteria = TourService.get_all_criteria()
        
        self.assertEqual(len(criteria), 2)
        self.assertEqual(criteria[0].name, 'Phong cảnh')
        self.assertEqual(criteria[1].name, 'Văn hóa')
    
    @patch('src.services.tour_service.execute_query')
    def test_get_tour_by_id(self, mock_execute):
        """Test getting tour by ID."""
        # Mock database response
        mock_execute.return_value = [
            {
                'id': 1,
                'name': 'Hạ Long - Cát Bà',
                'destination': 'Quảng Ninh',
                'duration': 3,
                'price': 4500000,
                'max_participants': 30,
                'difficulty_level': 'easy',
                'season': 'Quanh năm',
                'description': 'Tour đẹp',
                'image_url': None,
                'created_at': None,
                'updated_at': None,
                'scores': 'Phong cảnh:9.5|Văn hóa:7.0'
            }
        ]
        
        tour = TourService.get_tour_by_id(1)
        
        self.assertIsNotNone(tour)
        self.assertEqual(tour.name, 'Hạ Long - Cát Bà')
        self.assertEqual(tour.duration, 3)
        self.assertEqual(tour.get_criterion_score('Phong cảnh'), 9.5)
        self.assertEqual(tour.get_criterion_score('Văn hóa'), 7.0)


if __name__ == '__main__':
    unittest.main()

