"""Tests for AHP algorithm."""

import unittest
import numpy as np
from src.algorithms.ahp import AHPCalculator
from src.algorithms.validator import ConsistencyValidator


class TestAHP(unittest.TestCase):
    """Test AHP calculator."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.calculator = AHPCalculator()
        self.validator = ConsistencyValidator()
    
    def test_weights_sum_to_one(self):
        """Test that weights sum to 1."""
        # Create a simple comparison matrix
        matrix = np.array([
            [1, 3, 5],
            [1/3, 1, 2],
            [1/5, 1/2, 1]
        ])
        
        weights = self.calculator.calculate_weights_geometric_mean(matrix)
        
        # Check sum is approximately 1
        self.assertAlmostEqual(np.sum(weights), 1.0, places=6)
    
    def test_consistency_ratio(self):
        """Test consistency ratio calculation."""
        # Perfectly consistent matrix (derived from weights)
        weights = np.array([0.6, 0.3, 0.1])
        matrix = np.outer(weights, 1/weights)
        
        cr = self.validator.calculate_cr(matrix, weights)
        
        # CR should be very close to 0 for consistent matrix
        self.assertLess(cr, 0.01)
    
    def test_matrix_validation(self):
        """Test matrix validation."""
        # Valid matrix
        valid_matrix = np.array([
            [1, 3, 5],
            [1/3, 1, 2],
            [1/5, 1/2, 1]
        ])
        
        self.assertTrue(self.validator.validate_matrix(valid_matrix))
        
        # Invalid matrix (not reciprocal)
        invalid_matrix = np.array([
            [1, 3, 5],
            [1/2, 1, 2],  # Should be 1/3
            [1/5, 1/2, 1]
        ])
        
        self.assertFalse(self.validator.validate_matrix(invalid_matrix))
    
    def test_example_matrix(self):
        """Test example matrix generation."""
        matrix = self.calculator.create_example_matrix(6)
        
        # Check shape
        self.assertEqual(matrix.shape, (6, 6))
        
        # Check diagonal is 1
        np.testing.assert_array_almost_equal(np.diag(matrix), np.ones(6))
        
        # Check reciprocal property
        for i in range(6):
            for j in range(6):
                self.assertAlmostEqual(matrix[i][j] * matrix[j][i], 1.0, places=5)


if __name__ == '__main__':
    unittest.main()

