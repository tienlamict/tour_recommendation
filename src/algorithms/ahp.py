"""AHP (Analytic Hierarchy Process) implementation."""

import numpy as np
import logging
from typing import List, Dict, Tuple
from .validator import ConsistencyValidator

logger = logging.getLogger(__name__)


class AHPCalculator:
    """AHP calculator for multi-criteria decision making."""
    
    def __init__(self):
        """Initialize AHP calculator."""
        self.validator = ConsistencyValidator()
    
    def calculate_weights_geometric_mean(self, matrix: np.ndarray) -> np.ndarray:
        """Calculate weights using geometric mean method.
        
        This is the most commonly used method for AHP weight calculation.
        
        Args:
            matrix: Pairwise comparison matrix (n x n)
            
        Returns:
            Weight vector (normalized to sum = 1)
        """
        n = matrix.shape[0]
        
        # Calculate geometric mean of each row
        geometric_means = np.zeros(n)
        for i in range(n):
            product = np.prod(matrix[i, :])
            geometric_means[i] = product ** (1.0 / n)
        
        # Normalize to sum = 1
        weights = geometric_means / np.sum(geometric_means)
        
        logger.debug(f"Calculated weights (geometric mean): {weights}")
        return weights
    
    def calculate_weights_eigenvalue(self, matrix: np.ndarray) -> np.ndarray:
        """Calculate weights using eigenvalue method.
        
        This is Saaty's original method using the principal eigenvector.
        
        Args:
            matrix: Pairwise comparison matrix (n x n)
            
        Returns:
            Weight vector (normalized to sum = 1)
        """
        # Calculate eigenvalues and eigenvectors
        eigenvalues, eigenvectors = np.linalg.eig(matrix)
        
        # Find index of maximum eigenvalue
        max_index = np.argmax(eigenvalues.real)
        
        # Get corresponding eigenvector
        principal_eigenvector = eigenvectors[:, max_index].real
        
        # Normalize to sum = 1
        weights = principal_eigenvector / np.sum(principal_eigenvector)
        
        logger.debug(f"Calculated weights (eigenvalue): {weights}")
        return weights
    
    def build_pairwise_matrix(self, comparisons: Dict[Tuple[int, int], float], n: int) -> np.ndarray:
        """Build pairwise comparison matrix from comparison values.
        
        Args:
            comparisons: Dictionary of {(i, j): value} comparisons
            n: Size of matrix
            
        Returns:
            Pairwise comparison matrix
        """
        matrix = np.ones((n, n))
        
        for (i, j), value in comparisons.items():
            matrix[i][j] = value
            matrix[j][i] = 1.0 / value
        
        return matrix
    
    def calculate_criteria_weights(
        self,
        comparison_matrix: np.ndarray,
        method: str = 'geometric'
    ) -> Tuple[np.ndarray, float, bool]:
        """Calculate criteria weights from comparison matrix.
        
        Args:
            comparison_matrix: Pairwise comparison matrix
            method: 'geometric' or 'eigenvalue'
            
        Returns:
            Tuple of (weights, consistency_ratio, is_consistent)
        """
        # Validate matrix
        if not self.validator.validate_matrix(comparison_matrix):
            raise ValueError("Invalid comparison matrix")
        
        # Calculate weights
        if method == 'geometric':
            weights = self.calculate_weights_geometric_mean(comparison_matrix)
        elif method == 'eigenvalue':
            weights = self.calculate_weights_eigenvalue(comparison_matrix)
        else:
            raise ValueError(f"Unknown method: {method}")
        
        # Check consistency
        is_consistent, cr = self.validator.is_consistent(comparison_matrix, weights)
        
        logger.info(f"Criteria weights calculated: {weights}, CR={cr:.4f}")
        return weights, cr, is_consistent
    
    def calculate_alternative_scores(
        self,
        alternatives_data: List[Dict[str, float]],
        criteria_weights: np.ndarray,
        criteria_names: List[str]
    ) -> np.ndarray:
        """Calculate final scores for alternatives.
        
        Args:
            alternatives_data: List of dictionaries with criterion scores
            criteria_weights: Weight vector for criteria
            criteria_names: List of criterion names
            
        Returns:
            Array of final scores for each alternative
        """
        n_alternatives = len(alternatives_data)
        n_criteria = len(criteria_names)
        
        # Build score matrix (alternatives x criteria)
        score_matrix = np.zeros((n_alternatives, n_criteria))
        
        for i, alt_data in enumerate(alternatives_data):
            for j, criterion in enumerate(criteria_names):
                score_matrix[i, j] = alt_data.get(criterion, 0.0)
        
        # Normalize score matrix (each column to 0-1)
        normalized_matrix = np.zeros_like(score_matrix)
        for j in range(n_criteria):
            col_max = np.max(score_matrix[:, j])
            if col_max > 0:
                normalized_matrix[:, j] = score_matrix[:, j] / col_max
        
        # Calculate weighted scores
        final_scores = np.dot(normalized_matrix, criteria_weights)
        
        logger.info(f"Alternative scores calculated for {n_alternatives} alternatives")
        return final_scores
    
    def rank_alternatives(
        self,
        alternatives: List[str],
        scores: np.ndarray
    ) -> List[Tuple[str, float]]:
        """Rank alternatives by their scores.
        
        Args:
            alternatives: List of alternative names
            scores: Array of scores
            
        Returns:
            List of (alternative, score) tuples sorted by score (descending)
        """
        ranked = list(zip(alternatives, scores))
        ranked.sort(key=lambda x: x[1], reverse=True)
        
        logger.info(f"Alternatives ranked: Top 3 = {ranked[:3]}")
        return ranked
    
    @staticmethod
    def create_example_matrix(n: int = 6) -> np.ndarray:
        """Create an example comparison matrix for demonstration.
        
        Args:
            n: Size of matrix (default 6 for 6 criteria)
            
        Returns:
            Example pairwise comparison matrix
        """
        # Example: User prefers Scenery > Culture > Cuisine > Adventure > Relaxation > Shopping
        if n == 6:
            matrix = np.array([
                [1,   3,   5,   7,   5,   9],  # Phong cảnh
                [1/3, 1,   3,   5,   3,   7],  # Văn hóa
                [1/5, 1/3, 1,   3,   2,   5],  # Ẩm thực
                [1/7, 1/5, 1/3, 1,   1/2, 3],  # Mạo hiểm
                [1/5, 1/3, 1/2, 2,   1,   4],  # Thư giãn
                [1/9, 1/7, 1/5, 1/3, 1/4, 1]   # Mua sắm
            ])
        else:
            # Generic example for other sizes
            matrix = np.ones((n, n))
            for i in range(n):
                for j in range(i + 1, n):
                    value = (n - i) / (n - j + 1)
                    matrix[i][j] = value
                    matrix[j][i] = 1.0 / value
        
        return matrix

