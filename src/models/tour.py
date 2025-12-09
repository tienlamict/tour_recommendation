"""Tour and Criterion models."""

from dataclasses import dataclass
from typing import Dict, Optional
from datetime import datetime


@dataclass
class Criterion:
    """Criterion model."""
    id: int
    name: str
    description: Optional[str] = None
    icon: Optional[str] = None
    created_at: Optional[datetime] = None
    
    def __str__(self) -> str:
        return f"{self.icon} {self.name}" if self.icon else self.name


@dataclass
class Tour:
    """Tour model."""
    id: int
    name: str
    destination: str
    duration: int  # days
    price: float  # VND
    max_participants: int
    difficulty_level: str  # 'easy', 'moderate', 'hard'
    season: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    # Criterion scores (populated separately)
    criterion_scores: Dict[str, float] = None
    
    # AHP and TOPSIS scores (calculated)
    ahp_score: Optional[float] = None
    topsis_score: Optional[float] = None
    
    def __post_init__(self):
        """Initialize criterion_scores if None."""
        if self.criterion_scores is None:
            self.criterion_scores = {}
    
    def get_criterion_score(self, criterion_name: str) -> float:
        """Get score for a specific criterion.
        
        Args:
            criterion_name: Name of the criterion
            
        Returns:
            Score value (0-10)
        """
        return self.criterion_scores.get(criterion_name, 0.0)
    
    def set_criterion_score(self, criterion_name: str, score: float) -> None:
        """Set score for a specific criterion.
        
        Args:
            criterion_name: Name of the criterion
            score: Score value (0-10)
        """
        if not 0 <= score <= 10:
            raise ValueError(f"Score must be between 0 and 10, got {score}")
        self.criterion_scores[criterion_name] = score
    
    def get_price_display(self) -> str:
        """Get formatted price display.
        
        Returns:
            Formatted price string
        """
        if self.price >= 1_000_000:
            return f"{self.price / 1_000_000:.1f} triệu"
        else:
            return f"{self.price / 1_000:.0f}k"
    
    def get_difficulty_display(self) -> str:
        """Get difficulty level display with emoji.
        
        Returns:
            Formatted difficulty string
        """
        difficulty_map = {
            'easy': '⭐ Dễ',
            'moderate': '⭐⭐ Trung bình',
            'hard': '⭐⭐⭐ Khó'
        }
        return difficulty_map.get(self.difficulty_level, self.difficulty_level)
    
    def __str__(self) -> str:
        return f"{self.name} - {self.destination} ({self.duration} ngày)"
    
    def to_dict(self) -> dict:
        """Convert tour to dictionary.
        
        Returns:
            Dictionary representation
        """
        return {
            'id': self.id,
            'name': self.name,
            'destination': self.destination,
            'duration': self.duration,
            'price': self.price,
            'max_participants': self.max_participants,
            'difficulty_level': self.difficulty_level,
            'season': self.season,
            'description': self.description,
            'image_url': self.image_url,
            'criterion_scores': self.criterion_scores,
            'ahp_score': self.ahp_score,
            'topsis_score': self.topsis_score
        }

