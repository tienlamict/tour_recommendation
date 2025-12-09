"""Recommendation service combining AHP and TOPSIS."""

import numpy as np
import logging
from typing import List, Tuple, Dict

from ..models.tour import Tour
from ..models.preference import UserPreference
from ..algorithms.ahp import AHPCalculator
from ..algorithms.topsis import TOPSISCalculator

logger = logging.getLogger(__name__)


class RecommendationService:
    """Service for generating tour recommendations."""
    
    def __init__(self):
        """Initialize recommendation service."""
        self.ahp_calculator = AHPCalculator()
        self.topsis_calculator = TOPSISCalculator()
    
    def calculate_ahp_scores(
        self,
        tours: List[Tour],
        criteria_weights: np.ndarray,
        criteria_names: List[str]
    ) -> List[Tour]:
        """Calculate AHP scores for tours.
        
        Args:
            tours: List of tours
            criteria_weights: Weight vector for criteria
            criteria_names: List of criterion names
            
        Returns:
            Tours with AHP scores populated
        """
        # Build alternatives data
        alternatives_data = []
        for tour in tours:
            tour_data = {
                criterion: tour.get_criterion_score(criterion)
                for criterion in criteria_names
            }
            alternatives_data.append(tour_data)
        
        # Calculate AHP scores
        ahp_scores = self.ahp_calculator.calculate_alternative_scores(
            alternatives_data,
            criteria_weights,
            criteria_names
        )
        
        # Assign scores to tours
        for i, tour in enumerate(tours):
            tour.ahp_score = ahp_scores[i]
        
        logger.info(f"Calculated AHP scores for {len(tours)} tours")
        return tours
    
    def calculate_topsis_scores(
        self,
        tours: List[Tour],
        topsis_weights: Dict[str, float]
    ) -> List[Tour]:
        """Calculate TOPSIS scores for tours.
        
        Args:
            tours: List of tours (must have AHP scores)
            topsis_weights: Dictionary with keys 'ahp', 'price', 'duration'
            
        Returns:
            Tours with TOPSIS scores populated
        """
        # Build decision matrix: [AHP score, Price, Duration]
        decision_matrix = np.array([
            [tour.ahp_score, tour.price, tour.duration]
            for tour in tours
        ])
        
        # Weights for TOPSIS criteria
        weights = np.array([
            topsis_weights.get('ahp', 0.5),
            topsis_weights.get('price', 0.3),
            topsis_weights.get('duration', 0.2)
        ])
        
        # Normalize weights
        weights = weights / np.sum(weights)
        
        # Benefit criteria: [True (AHP), False (Price - lower is better), False (Duration - lower is better)]
        benefit_criteria = [True, False, False]
        
        # Calculate TOPSIS scores
        topsis_scores, ranked_list = self.topsis_calculator.rank(
            decision_matrix,
            weights,
            benefit_criteria
        )
        
        # Assign scores to tours
        for i, tour in enumerate(tours):
            tour.topsis_score = topsis_scores[i]
        
        logger.info(f"Calculated TOPSIS scores for {len(tours)} tours")
        return tours
    
    def recommend_tours(
        self,
        tours: List[Tour],
        user_preference: UserPreference,
        criteria_names: List[str],
        top_n: int = None
    ) -> List[Tour]:
        """Generate tour recommendations.
        
        Args:
            tours: List of available tours
            user_preference: User preference with comparison matrix and weights
            criteria_names: List of criterion names
            top_n: Number of top tours to return (None for all)
            
        Returns:
            Ranked list of tours
        """
        logger.info(f"Generating recommendations for {len(tours)} tours")
        
        # Step 1: Calculate AHP scores
        tours = self.calculate_ahp_scores(
            tours,
            user_preference.criteria_weights,
            criteria_names
        )
        
        # Step 2: Calculate TOPSIS scores
        tours = self.calculate_topsis_scores(
            tours,
            user_preference.topsis_weights
        )
        
        # Step 3: Sort by TOPSIS score (descending)
        tours.sort(key=lambda t: t.topsis_score, reverse=True)
        
        # Step 4: Return top N
        if top_n:
            tours = tours[:top_n]
        
        logger.info(f"Top recommendation: {tours[0].name} (TOPSIS: {tours[0].topsis_score:.4f})")
        return tours
    
    def explain_recommendation(
        self,
        tour: Tour,
        criteria_names: List[str],
        criteria_weights: np.ndarray
    ) -> str:
        """Generate explanation for why a tour was recommended.
        
        Args:
            tour: Tour to explain
            criteria_names: List of criterion names
            criteria_weights: Criteria weights from AHP
            
        Returns:
            Explanation text
        """
        # Find top criteria for this tour
        weighted_scores = []
        for i, criterion in enumerate(criteria_names):
            score = tour.get_criterion_score(criterion)
            weight = criteria_weights[i]
            weighted_scores.append((criterion, score, weight, score * weight))
        
        # Sort by weighted score
        weighted_scores.sort(key=lambda x: x[3], reverse=True)
        
        # Build explanation
        top_criterion = weighted_scores[0]
        explanation = f"Tour này được đề xuất vì:\n\n"
        explanation += f"1. Bạn ưu tiên tiêu chí '{top_criterion[0]}' (trọng số: {top_criterion[2]:.2%})\n"
        explanation += f"   và tour này có điểm cao về '{top_criterion[0]}' ({top_criterion[1]:.1f}/10)\n\n"
        
        # Add price info
        if tour.price < 4_000_000:
            price_desc = "giá rẻ"
        elif tour.price < 7_000_000:
            price_desc = "giá vừa phải"
        else:
            price_desc = "cao cấp"
        
        explanation += f"2. Tour có {price_desc} ({tour.get_price_display()})\n\n"
        
        # Add duration info
        if tour.duration <= 2:
            duration_desc = "ngắn ngày, phù hợp cho cuối tuần"
        elif tour.duration <= 4:
            duration_desc = "trung bình, phù hợp cho kỳ nghỉ"
        else:
            duration_desc = "dài ngày, trải nghiệm đầy đủ"
        
        explanation += f"3. Thời gian {duration_desc} ({tour.duration} ngày)\n\n"
        
        # Add top 3 criteria scores
        explanation += "Điểm mạnh của tour:\n"
        for i, (criterion, score, weight, _) in enumerate(weighted_scores[:3], 1):
            explanation += f"  • {criterion}: {score:.1f}/10\n"
        
        return explanation
    
    def compare_tours(
        self,
        tour1: Tour,
        tour2: Tour,
        criteria_names: List[str]
    ) -> Dict[str, any]:
        """Compare two tours.
        
        Args:
            tour1: First tour
            tour2: Second tour
            criteria_names: List of criterion names
            
        Returns:
            Comparison dictionary
        """
        comparison = {
            'tour1': tour1.name,
            'tour2': tour2.name,
            'criteria_comparison': {},
            'price_comparison': {
                'tour1': tour1.price,
                'tour2': tour2.price,
                'difference': tour2.price - tour1.price,
                'cheaper': tour1.name if tour1.price < tour2.price else tour2.name
            },
            'duration_comparison': {
                'tour1': tour1.duration,
                'tour2': tour2.duration,
                'difference': tour2.duration - tour1.duration,
                'shorter': tour1.name if tour1.duration < tour2.duration else tour2.name
            },
            'scores': {
                'tour1': {
                    'ahp': tour1.ahp_score,
                    'topsis': tour1.topsis_score
                },
                'tour2': {
                    'ahp': tour2.ahp_score,
                    'topsis': tour2.topsis_score
                }
            }
        }
        
        # Compare criteria scores
        for criterion in criteria_names:
            score1 = tour1.get_criterion_score(criterion)
            score2 = tour2.get_criterion_score(criterion)
            comparison['criteria_comparison'][criterion] = {
                'tour1': score1,
                'tour2': score2,
                'difference': score2 - score1,
                'better': tour1.name if score1 > score2 else tour2.name
            }
        
        return comparison

