"""User preference model."""

import json
import numpy as np
from dataclasses import dataclass, field
from typing import Dict, Optional, List
from datetime import datetime


@dataclass
class UserPreference:
    """User preference model for storing AHP comparisons."""
    
    id: Optional[int] = None
    user_name: Optional[str] = None
    comparison_matrix: np.ndarray = None
    criteria_weights: np.ndarray = None
    consistency_ratio: Optional[float] = None
    topsis_weights: Dict[str, float] = field(default_factory=dict)
    created_at: Optional[datetime] = None
    
    def to_json(self) -> str:
        """Convert preference to JSON string.
        
        Returns:
            JSON string representation
        """
        data = {
            'comparison_matrix': self.comparison_matrix.tolist() if self.comparison_matrix is not None else None,
            'criteria_weights': self.criteria_weights.tolist() if self.criteria_weights is not None else None,
            'consistency_ratio': self.consistency_ratio,
            'topsis_weights': self.topsis_weights
        }
        return json.dumps(data)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'UserPreference':
        """Create preference from JSON string.
        
        Args:
            json_str: JSON string
            
        Returns:
            UserPreference instance
        """
        data = json.loads(json_str)
        
        comparison_matrix = np.array(data['comparison_matrix']) if data.get('comparison_matrix') else None
        criteria_weights = np.array(data['criteria_weights']) if data.get('criteria_weights') else None
        
        return cls(
            comparison_matrix=comparison_matrix,
            criteria_weights=criteria_weights,
            consistency_ratio=data.get('consistency_ratio'),
            topsis_weights=data.get('topsis_weights', {})
        )
    
    def to_dict(self) -> dict:
        """Convert to dictionary.
        
        Returns:
            Dictionary representation
        """
        return {
            'id': self.id,
            'user_name': self.user_name,
            'comparison_matrix': self.comparison_matrix.tolist() if self.comparison_matrix is not None else None,
            'criteria_weights': self.criteria_weights.tolist() if self.criteria_weights is not None else None,
            'consistency_ratio': self.consistency_ratio,
            'topsis_weights': self.topsis_weights,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def is_valid(self) -> bool:
        """Check if preference is valid.
        
        Returns:
            True if valid, False otherwise
        """
        if self.comparison_matrix is None or self.criteria_weights is None:
            return False
        
        if self.consistency_ratio is not None and self.consistency_ratio >= 0.1:
            return False
        
        return True
    
    def get_criteria_weight(self, criterion_index: int) -> float:
        """Get weight for a specific criterion.
        
        Args:
            criterion_index: Index of the criterion
            
        Returns:
            Weight value
        """
        if self.criteria_weights is None or criterion_index >= len(self.criteria_weights):
            return 0.0
        return self.criteria_weights[criterion_index]
    
    def get_topsis_weight(self, key: str, default: float = 0.0) -> float:
        """Get TOPSIS weight for a key.
        
        Args:
            key: Weight key (e.g., 'ahp', 'price', 'duration')
            default: Default value if key not found
            
        Returns:
            Weight value
        """
        return self.topsis_weights.get(key, default)

