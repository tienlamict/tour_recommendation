"""TOPSIS (Technique for Order Preference by Similarity to Ideal Solution) implementation."""

import numpy as np
import logging
from typing import List, Tuple, Dict

logger = logging.getLogger(__name__)


class TOPSISCalculator:
    """TOPSIS calculator for ranking alternatives."""
    
    def __init__(self):
        """Initialize TOPSIS calculator."""
        pass
    
    def normalize_matrix(
        self,
        decision_matrix: np.ndarray,
        benefit_criteria: List[bool]
    ) -> np.ndarray:
        """Normalize decision matrix.
        
        For benefit criteria: higher is better (normalize normally)
        For cost criteria: lower is better (invert values)
        
        Args:
            decision_matrix: Matrix of alternatives x criteria
            benefit_criteria: List of booleans indicating if criterion is benefit (True) or cost (False)
            
        Returns:
            Normalized matrix
        """
        n_alternatives, n_criteria = decision_matrix.shape
        normalized = np.zeros_like(decision_matrix, dtype=float)
        
        for j in range(n_criteria):
            column = decision_matrix[:, j]
            
            # Calculate norm for this column
            norm = np.sqrt(np.sum(column ** 2))
            
            if norm > 0:
                if benefit_criteria[j]:
                    # Benefit criterion: normalize normally
                    normalized[:, j] = column / norm
                else:
                    # Cost criterion: invert and normalize
                    # Use (max - value) to convert cost to benefit
                    max_val = np.max(column)
                    inverted = max_val - column
                    norm_inverted = np.sqrt(np.sum(inverted ** 2))
                    if norm_inverted > 0:
                        normalized[:, j] = inverted / norm_inverted
                    else:
                        normalized[:, j] = inverted
            else:
                normalized[:, j] = column
        
        logger.debug(f"Matrix normalized with benefit criteria: {benefit_criteria}")
        return normalized
    
    def apply_weights(
        self,
        normalized_matrix: np.ndarray,
        weights: np.ndarray
    ) -> np.ndarray:
        """Apply weights to normalized matrix.
        
        Args:
            normalized_matrix: Normalized decision matrix
            weights: Weight vector for criteria
            
        Returns:
            Weighted normalized matrix
        """
        # Validate weights sum to 1
        weight_sum = np.sum(weights)
        if not np.isclose(weight_sum, 1.0, rtol=1e-5):
            logger.warning(f"Weights sum to {weight_sum}, normalizing...")
            weights = weights / weight_sum
        
        weighted_matrix = normalized_matrix * weights
        logger.debug(f"Weights applied: {weights}")
        return weighted_matrix
    
    def find_ideal_solutions(
        self,
        weighted_matrix: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Find ideal positive and negative solutions.
        
        Args:
            weighted_matrix: Weighted normalized matrix
            
        Returns:
            Tuple of (ideal_positive, ideal_negative)
        """
        # Ideal positive: maximum value for each criterion
        ideal_positive = np.max(weighted_matrix, axis=0)
        
        # Ideal negative: minimum value for each criterion
        ideal_negative = np.min(weighted_matrix, axis=0)
        
        logger.debug(f"Ideal positive: {ideal_positive}")
        logger.debug(f"Ideal negative: {ideal_negative}")
        
        return ideal_positive, ideal_negative
    
    def calculate_distances(
        self,
        weighted_matrix: np.ndarray,
        ideal_positive: np.ndarray,
        ideal_negative: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Calculate Euclidean distances to ideal solutions.
        
        Args:
            weighted_matrix: Weighted normalized matrix
            ideal_positive: Ideal positive solution
            ideal_negative: Ideal negative solution
            
        Returns:
            Tuple of (distances_to_positive, distances_to_negative)
        """
        n_alternatives = weighted_matrix.shape[0]
        
        distances_positive = np.zeros(n_alternatives)
        distances_negative = np.zeros(n_alternatives)
        
        for i in range(n_alternatives):
            # Distance to ideal positive
            diff_positive = weighted_matrix[i, :] - ideal_positive
            distances_positive[i] = np.sqrt(np.sum(diff_positive ** 2))
            
            # Distance to ideal negative
            diff_negative = weighted_matrix[i, :] - ideal_negative
            distances_negative[i] = np.sqrt(np.sum(diff_negative ** 2))
        
        logger.debug(f"Distances calculated for {n_alternatives} alternatives")
        return distances_positive, distances_negative
    
    def calculate_scores(
        self,
        distances_positive: np.ndarray,
        distances_negative: np.ndarray
    ) -> np.ndarray:
        """Calculate TOPSIS scores.
        
        Score = S- / (S+ + S-)
        
        Args:
            distances_positive: Distances to ideal positive
            distances_negative: Distances to ideal negative
            
        Returns:
            TOPSIS scores (0 to 1, higher is better)
        """
        # Avoid division by zero
        denominator = distances_positive + distances_negative
        scores = np.where(
            denominator > 0,
            distances_negative / denominator,
            0.5  # If both distances are 0, score is neutral
        )
        
        logger.info(f"TOPSIS scores calculated: min={np.min(scores):.4f}, max={np.max(scores):.4f}")
        return scores
    
    def rank(
        self,
        decision_matrix: np.ndarray,
        weights: np.ndarray,
        benefit_criteria: List[bool],
        alternative_names: List[str] = None
    ) -> Tuple[np.ndarray, List[Tuple[int, float]]]:
        """Perform complete TOPSIS ranking.
        
        Args:
            decision_matrix: Matrix of alternatives x criteria
            weights: Weight vector for criteria
            benefit_criteria: List indicating benefit (True) or cost (False) criteria
            alternative_names: Optional list of alternative names
            
        Returns:
            Tuple of (scores, ranked_list)
            where ranked_list is [(index, score), ...] sorted by score descending
        """
        logger.info(f"Starting TOPSIS ranking for {decision_matrix.shape[0]} alternatives")
        
        # Step 1: Normalize matrix
        normalized = self.normalize_matrix(decision_matrix, benefit_criteria)
        
        # Step 2: Apply weights
        weighted = self.apply_weights(normalized, weights)
        
        # Step 3: Find ideal solutions
        ideal_pos, ideal_neg = self.find_ideal_solutions(weighted)
        
        # Step 4: Calculate distances
        dist_pos, dist_neg = self.calculate_distances(weighted, ideal_pos, ideal_neg)
        
        # Step 5: Calculate scores
        scores = self.calculate_scores(dist_pos, dist_neg)
        
        # Step 6: Rank alternatives
        ranked_indices = np.argsort(scores)[::-1]  # Descending order
        ranked_list = [(idx, scores[idx]) for idx in ranked_indices]
        
        if alternative_names:
            logger.info(f"Top 3 alternatives: {[(alternative_names[idx], score) for idx, score in ranked_list[:3]]}")
        else:
            logger.info(f"Top 3 alternatives: {ranked_list[:3]}")
        
        return scores, ranked_list
    
    def explain_ranking(
        self,
        alternative_idx: int,
        decision_matrix: np.ndarray,
        weights: np.ndarray,
        criteria_names: List[str],
        benefit_criteria: List[bool]
    ) -> Dict[str, any]:
        """Generate explanation for why an alternative was ranked.
        
        Args:
            alternative_idx: Index of the alternative
            decision_matrix: Original decision matrix
            weights: Criteria weights
            criteria_names: Names of criteria
            benefit_criteria: Benefit/cost indicators
            
        Returns:
            Dictionary with explanation details
        """
        n_criteria = len(criteria_names)
        alternative_values = decision_matrix[alternative_idx, :]
        
        # Find strongest criteria
        weighted_values = alternative_values * weights
        strongest_idx = np.argmax(weighted_values)
        
        explanation = {
            'strongest_criterion': criteria_names[strongest_idx],
            'strongest_value': alternative_values[strongest_idx],
            'strongest_weight': weights[strongest_idx],
            'criterion_scores': {
                criteria_names[i]: {
                    'value': alternative_values[i],
                    'weight': weights[i],
                    'weighted_value': weighted_values[i],
                    'is_benefit': benefit_criteria[i]
                }
                for i in range(n_criteria)
            }
        }
        
        return explanation

