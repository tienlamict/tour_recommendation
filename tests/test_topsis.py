"""Tests for TOPSIS algorithm."""

import unittest
import numpy as np
from src.algorithms.topsis import TOPSISCalculator


class TestTOPSIS(unittest.TestCase):
    """Test TOPSIS calculator."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.calculator = TOPSISCalculator()
    
    def test_normalize_matrix(self):
        """Test matrix normalization."""
        # Sample decision matrix
        matrix = np.array([
            [8, 7, 2],
            [5, 3, 4],
            [7, 5, 6]
        ])
        
        benefit_criteria = [True, True, False]  # Third is cost
        
        normalized = self.calculator.normalize_matrix(matrix, benefit_criteria)
        
        # Check that normalized values are between 0 and 1
        self.assertTrue(np.all(normalized >= 0))
        self.assertTrue(np.all(normalized <= 1))
    
    def test_scores_range(self):
        """Test that TOPSIS scores are in [0, 1] range."""
        # Sample data
        decision_matrix = np.array([
            [8, 100, 3],
            [6, 80, 4],
            [9, 120, 2],
            [7, 90, 5]
        ])
        
        weights = np.array([0.5, 0.3, 0.2])
        benefit_criteria = [True, False, False]  # AHP benefit, Price cost, Duration cost
        
        scores, ranked = self.calculator.rank(
            decision_matrix,
            weights,
            benefit_criteria
        )
        
        # Check scores are in valid range
        self.assertTrue(np.all(scores >= 0))
        self.assertTrue(np.all(scores <= 1))
        
        # Check ranking is descending
        for i in range(len(ranked) - 1):
            self.assertGreaterEqual(scores[ranked[i][0]], scores[ranked[i+1][0]])
    
    def test_weights_normalization(self):
        """Test that weights are normalized if they don't sum to 1."""
        decision_matrix = np.array([
            [8, 100, 3],
            [6, 80, 4]
        ])
        
        # Weights that don't sum to 1
        weights = np.array([2, 1, 1])
        benefit_criteria = [True, False, False]
        
        # Should not raise error and should normalize internally
        scores, ranked = self.calculator.rank(
            decision_matrix,
            weights,
            benefit_criteria
        )
        
        self.assertEqual(len(scores), 2)
    
    def test_ideal_solutions(self):
        """Test ideal solution calculation."""
        weighted_matrix = np.array([
            [0.5, 0.3, 0.2],
            [0.4, 0.4, 0.3],
            [0.6, 0.2, 0.1]
        ])
        
        ideal_pos, ideal_neg = self.calculator.find_ideal_solutions(weighted_matrix)
        
        # Ideal positive should be max of each column
        np.testing.assert_array_almost_equal(
            ideal_pos,
            np.max(weighted_matrix, axis=0)
        )
        
        # Ideal negative should be min of each column
        np.testing.assert_array_almost_equal(
            ideal_neg,
            np.min(weighted_matrix, axis=0)
        )


if __name__ == '__main__':
    unittest.main()

