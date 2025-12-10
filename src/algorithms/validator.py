"""Consistency validation for AHP matrices."""

import numpy as np
import logging
from typing import Tuple

logger = logging.getLogger(__name__)


class ConsistencyValidator:
    """Validator for AHP matrix consistency."""
    
    # Random Index (RI) values for different matrix sizes
    # Source: Saaty, T.L. (1980)
    RANDOM_INDEX = {
        1: 0.00,
        2: 0.00,
        3: 0.58,
        4: 0.90,
        5: 1.12,
        6: 1.24,
        7: 1.32,
        8: 1.41,
        9: 1.45,
        10: 1.49,
        11: 1.51,
        12: 1.48,
        13: 1.56,
        14: 1.57,
        15: 1.59
    }
    
    @staticmethod
    def calculate_lambda_max(matrix: np.ndarray, weights: np.ndarray) -> float:
        """Calculate the maximum eigenvalue (lambda max).
        
        Args:
            matrix: Pairwise comparison matrix
            weights: Weight vector
            
        Returns:
            Lambda max value
        """
        n = len(weights)
        weighted_sum = np.dot(matrix, weights)
        lambda_max = np.sum(weighted_sum / weights) / n
        return lambda_max
    
    @staticmethod
    def calculate_ci(matrix: np.ndarray, weights: np.ndarray) -> float:
        """Calculate Consistency Index (CI).
        
        CI = (λmax - n) / (n - 1)
        
        Args:
            matrix: Pairwise comparison matrix
            weights: Weight vector
            
        Returns:
            Consistency Index
        """
        n = len(weights)
        if n <= 1:
            return 0.0
        
        lambda_max = ConsistencyValidator.calculate_lambda_max(matrix, weights)
        ci = (lambda_max - n) / (n - 1)
        return ci
    
    @staticmethod
    def calculate_cr(matrix: np.ndarray, weights: np.ndarray) -> float:
        """Calculate Consistency Ratio (CR).
        
        CR = CI / RI
        
        Args:
            matrix: Pairwise comparison matrix
            weights: Weight vector
            
        Returns:
            Consistency Ratio
        """
        n = len(weights)
        if n <= 2:
            return 0.0
        
        ci = ConsistencyValidator.calculate_ci(matrix, weights)
        ri = ConsistencyValidator.RANDOM_INDEX.get(n, 1.49)
        cr = ci / ri if ri > 0 else 0.0
        
        logger.debug(f"Consistency check: n={n}, CI={ci:.4f}, RI={ri:.4f}, CR={cr:.4f}")
        return cr
    
    @staticmethod
    def is_consistent(matrix: np.ndarray, weights: np.ndarray, threshold: float = 0.1) -> Tuple[bool, float]:
        """Check if matrix is consistent.
        
        Args:
            matrix: Pairwise comparison matrix
            weights: Weight vector
            threshold: Maximum acceptable CR (default 0.1)
            
        Returns:
            Tuple of (is_consistent, cr_value)
        """
        cr = ConsistencyValidator.calculate_cr(matrix, weights)
        is_consistent = cr < threshold
        
        if is_consistent:
            logger.info(f"Matrix is consistent: CR={cr:.4f} < {threshold}")
        else:
            logger.warning(f"Matrix is inconsistent: CR={cr:.4f} >= {threshold}")
        
        return is_consistent, cr
    
    @staticmethod
    def validate_matrix(matrix: np.ndarray) -> bool:
        """Validate pairwise comparison matrix structure.
        
        Args:
            matrix: Matrix to validate
            
        Returns:
            True if valid, False otherwise
        """
        # Check if square matrix
        if matrix.shape[0] != matrix.shape[1]:
            logger.error("Matrix is not square")
            return False
        
        n = matrix.shape[0]
        
        # Check diagonal elements are 1
        if not np.allclose(np.diag(matrix), np.ones(n)):
            logger.error("Diagonal elements are not all 1")
            return False
        
        # Check reciprocal property: a[i][j] = 1 / a[j][i]
        for i in range(n):
            for j in range(n):
                if not np.isclose(matrix[i][j] * matrix[j][i], 1.0, rtol=1e-5):
                    logger.error(f"Reciprocal property violated at ({i},{j})")
                    return False
        
        # Check for positive values
        if np.any(matrix <= 0):
            logger.error("Matrix contains non-positive values")
            return False
        
        logger.debug("Matrix validation passed")
        return True
    
    @staticmethod
    def find_inconsistencies(matrix: np.ndarray, criteria_names: list = None) -> list:
        """Find inconsistencies in comparison matrix.
        
        Checks for violations of transitivity: if A > B and B > C, then A should be > C.
        
        Args:
            matrix: Comparison matrix
            criteria_names: Optional list of criterion names
            
        Returns:
            List of inconsistency descriptions
        """
        n = len(matrix)
        if criteria_names is None:
            criteria_names = [f"Tiêu chí {i+1}" for i in range(n)]
        
        inconsistencies = []
        threshold = 0.5  # Threshold for significant inconsistency
        
        # Check transitivity for all triplets (A, B, C)
        for i in range(n):
            for j in range(i + 1, n):
                for k in range(j + 1, n):
                    # Get comparisons
                    a_ij = matrix[i][j]  # A vs B
                    a_jk = matrix[j][k]  # B vs C
                    a_ik = matrix[i][k]  # A vs C (should be approximately a_ij * a_jk)
                    
                    # Expected value
                    expected = a_ij * a_jk
                    actual = a_ik
                    
                    # Calculate inconsistency ratio
                    if expected > 0 and actual > 0:
                        ratio = actual / expected
                        
                        # Check if significantly different
                        if ratio > 2.0 or ratio < 0.5:
                            # Determine which criterion is stronger
                            if a_ij > 1:
                                a_str = criteria_names[i]
                                b_str = criteria_names[j]
                                a_vs_b = f"{a_str} > {b_str}"
                            else:
                                a_str = criteria_names[j]
                                b_str = criteria_names[i]
                                a_vs_b = f"{b_str} > {a_str}"
                            
                            if a_jk > 1:
                                b_str2 = criteria_names[j]
                                c_str = criteria_names[k]
                                b_vs_c = f"{b_str2} > {c_str}"
                            else:
                                b_str2 = criteria_names[k]
                                c_str = criteria_names[j]
                                b_vs_c = f"{c_str} > {b_str2}"
                            
                            if a_ik > 1:
                                a_str2 = criteria_names[i]
                                c_str2 = criteria_names[k]
                                a_vs_c = f"{a_str2} > {c_str2}"
                            else:
                                a_str2 = criteria_names[k]
                                c_str2 = criteria_names[i]
                                a_vs_c = f"{c_str2} > {a_str2}"
                            
                            inconsistencies.append({
                                'triplet': (criteria_names[i], criteria_names[j], criteria_names[k]),
                                'comparisons': {
                                    f"{criteria_names[i]} vs {criteria_names[j]}": a_ij,
                                    f"{criteria_names[j]} vs {criteria_names[k]}": a_jk,
                                    f"{criteria_names[i]} vs {criteria_names[k]}": a_ik
                                },
                                'expected': expected,
                                'actual': actual,
                                'ratio': ratio,
                                'description': (
                                    f"Mâu thuẫn: {a_vs_b} ({a_ij:.2f}) và {b_vs_c} ({a_jk:.2f}) "
                                    f"nhưng {a_vs_c} ({a_ik:.2f}). "
                                    f"Kỳ vọng: {expected:.2f}, Thực tế: {actual:.2f}"
                                )
                            })
        
        return inconsistencies

