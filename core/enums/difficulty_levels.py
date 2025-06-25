"""
Difficulty level enumerations for the question generation system.

This module defines the standardized difficulty levels used across
all question types and provides utilities for difficulty handling.
"""

from enum import Enum
from typing import List, Tuple, Optional


class DifficultyLevel(Enum):
    """Question difficulty levels on a 1-5 scale."""
    
    VERY_EASY = 1
    EASY = 2 
    MEDIUM = 3
    HARD = 4
    VERY_HARD = 5
    
    @classmethod
    def from_int(cls, value: int) -> 'DifficultyLevel':
        """
        Create DifficultyLevel from integer value.
        
        Args:
            value: Integer difficulty level (1-5)
            
        Returns:
            DifficultyLevel enum value
            
        Raises:
            ValueError: If value is not in valid range
        """
        if not isinstance(value, int) or value < 1 or value > 5:
            raise ValueError(f"Invalid difficulty level: {value}. Must be integer 1-5")
            
        for level in cls:
            if level.value == value:
                return level
                
        raise ValueError(f"Invalid difficulty level: {value}")
    
    @classmethod
    def from_string(cls, value: str) -> 'DifficultyLevel':
        """
        Create DifficultyLevel from string value.
        
        Args:
            value: String representation of difficulty level
            
        Returns:
            DifficultyLevel enum value
            
        Raises:
            ValueError: If value is not a valid difficulty level
        """
        # Handle numeric strings
        if value.isdigit():
            return cls.from_int(int(value))
            
        # Handle name-based strings
        name_mapping = {
            'very_easy': cls.VERY_EASY,
            'veryeasy': cls.VERY_EASY,
            'very easy': cls.VERY_EASY,
            '1': cls.VERY_EASY,
            'easy': cls.EASY,
            '2': cls.EASY,
            'medium': cls.MEDIUM,
            'med': cls.MEDIUM,
            '3': cls.MEDIUM,
            'hard': cls.HARD,
            '4': cls.HARD,
            'very_hard': cls.VERY_HARD,
            'veryhard': cls.VERY_HARD,
            'very hard': cls.VERY_HARD,
            'expert': cls.VERY_HARD,
            '5': cls.VERY_HARD
        }
        
        value_lower = value.lower().replace('-', '_').replace(' ', '_')
        
        if value_lower in name_mapping:
            return name_mapping[value_lower]
            
        for level in cls:
            if level.name.lower() == value_lower:
                return level
                
        raise ValueError(f"Invalid difficulty level: {value}")
    
    @classmethod
    def get_all_levels(cls) -> List['DifficultyLevel']:
        """Get all difficulty levels in order."""
        return [cls.VERY_EASY, cls.EASY, cls.MEDIUM, cls.HARD, cls.VERY_HARD]
    
    @classmethod
    def get_range(cls, min_level: 'DifficultyLevel', max_level: 'DifficultyLevel') -> List['DifficultyLevel']:
        """
        Get difficulty levels within a range.
        
        Args:
            min_level: Minimum difficulty level
            max_level: Maximum difficulty level
            
        Returns:
            List of difficulty levels in range
        """
        all_levels = cls.get_all_levels()
        min_idx = all_levels.index(min_level)
        max_idx = all_levels.index(max_level)
        
        if min_idx > max_idx:
            min_idx, max_idx = max_idx, min_idx
            
        return all_levels[min_idx:max_idx + 1]
    
    @property
    def display_name(self) -> str:
        """Human-readable difficulty name."""
        return self.name.replace('_', ' ').title()
    
    @property
    def short_name(self) -> str:
        """Short abbreviation for difficulty."""
        abbreviations = {
            self.VERY_EASY: "VE",
            self.EASY: "E",
            self.MEDIUM: "M", 
            self.HARD: "H",
            self.VERY_HARD: "VH"
        }
        return abbreviations.get(self, str(self.value))
    
    @property
    def percentile_range(self) -> Tuple[int, int]:
        """Approximate percentile range for this difficulty level."""
        percentile_mapping = {
            self.VERY_EASY: (0, 20),
            self.EASY: (20, 40),
            self.MEDIUM: (40, 60),
            self.HARD: (60, 80),
            self.VERY_HARD: (80, 100)
        }
        return percentile_mapping.get(self, (0, 100))
    
    @property
    def description(self) -> str:
        """Detailed description of difficulty level."""
        descriptions = {
            self.VERY_EASY: "Basic concepts, straightforward application",
            self.EASY: "Simple problem-solving, minimal complexity",
            self.MEDIUM: "Moderate complexity, multiple steps required",
            self.HARD: "Complex problem-solving, advanced concepts",
            self.VERY_HARD: "Expert level, highly complex reasoning"
        }
        return descriptions.get(self, "Unknown difficulty level")
    
    def next_level(self) -> Optional['DifficultyLevel']:
        """Get the next higher difficulty level."""
        if self.value < 5:
            return DifficultyLevel.from_int(self.value + 1)
        return None
    
    def prev_level(self) -> Optional['DifficultyLevel']:
        """Get the next lower difficulty level."""
        if self.value > 1:
            return DifficultyLevel.from_int(self.value - 1)
        return None
    
    def __str__(self) -> str:
        """String representation of difficulty level."""
        return str(self.value)
    
    def __int__(self) -> int:
        """Integer representation of difficulty level."""
        return self.value
    
    def __lt__(self, other: 'DifficultyLevel') -> bool:
        """Compare difficulty levels."""
        return self.value < other.value
    
    def __le__(self, other: 'DifficultyLevel') -> bool:
        """Compare difficulty levels."""
        return self.value <= other.value
    
    def __gt__(self, other: 'DifficultyLevel') -> bool:
        """Compare difficulty levels."""
        return self.value > other.value
    
    def __ge__(self, other: 'DifficultyLevel') -> bool:
        """Compare difficulty levels."""
        return self.value >= other.value