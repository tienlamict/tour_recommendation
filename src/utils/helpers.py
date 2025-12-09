"""Helper utility functions."""

import re
from typing import Union
from fractions import Fraction


def format_currency(amount: float) -> str:
    """Format amount as Vietnamese currency.
    
    Args:
        amount: Amount in VND
        
    Returns:
        Formatted currency string
    """
    if amount >= 1_000_000:
        return f"{amount / 1_000_000:.1f} triệu"
    elif amount >= 1_000:
        return f"{amount / 1_000:.0f}k"
    else:
        return f"{amount:.0f}"


def parse_fraction(value: str) -> float:
    """Parse fraction string to float.
    
    Args:
        value: String like "1/3", "5", "0.5"
        
    Returns:
        Float value
        
    Examples:
        >>> parse_fraction("1/3")
        0.333...
        >>> parse_fraction("5")
        5.0
    """
    value = value.strip()
    
    # Try to parse as fraction (e.g., "1/3")
    if '/' in value:
        try:
            frac = Fraction(value)
            return float(frac)
        except (ValueError, ZeroDivisionError):
            raise ValueError(f"Invalid fraction: {value}")
    
    # Try to parse as float
    try:
        return float(value)
    except ValueError:
        raise ValueError(f"Invalid number: {value}")


def validate_saaty_value(value: float, min_val: float = 1/9, max_val: float = 9) -> bool:
    """Validate if value is within Saaty scale range.
    
    Args:
        value: Value to validate
        min_val: Minimum allowed value
        max_val: Maximum allowed value
        
    Returns:
        True if valid, False otherwise
    """
    return min_val <= value <= max_val


def truncate_text(text: str, max_length: int = 50) -> str:
    """Truncate text to maximum length with ellipsis.
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        
    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."


def validate_email(email: str) -> bool:
    """Validate email format.
    
    Args:
        email: Email address
        
    Returns:
        True if valid email format
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

