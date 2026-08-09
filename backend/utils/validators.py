import re
from typing import Optional, List
from urllib.parse import urlparse

class InputValidator:
    """Utility class for input validation and sanitization"""
    
    @staticmethod
    def sanitize_string(input_string: Optional[str], max_length: int = 1000) -> Optional[str]:
        """
        Sanitize string input by limiting length and removing potentially dangerous characters.
        
        Args:
            input_string: The string to sanitize
            max_length: Maximum allowed length
            
        Returns:
            Sanitized string or None if input is invalid
        """
        if not input_string:
            return None
            
        if not isinstance(input_string, str):
            return None
            
        # Remove null bytes and other control characters
        sanitized = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', input_string)
        
        # Limit length
        if len(sanitized) > max_length:
            return sanitized[:max_length]
            
        return sanitized.strip()
    
    @staticmethod
    def validate_url(url: Optional[str]) -> bool:
        """
        Validate URL format.
        
        Args:
            url: URL string to validate
            
        Returns:
            True if URL is valid, False otherwise
        """
        if not url:
            return False
            
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False
    
    @staticmethod
    def validate_integer(value: Optional[int], min_val: Optional[int] = None, max_val: Optional[int] = None) -> bool:
        """
        Validate integer input within optional bounds.
        
        Args:
            value: Integer value to validate
            min_val: Minimum allowed value (inclusive)
            max_val: Maximum allowed value (inclusive)
            
        Returns:
            True if integer is valid, False otherwise
        """
        if value is None:
            return False
            
        if not isinstance(value, int):
            return False
            
        if min_val is not None and value < min_val:
            return False
            
        if max_val is not None and value > max_val:
            return False
            
        return True
    
    @staticmethod
    def sanitize_city_name(city: Optional[str]) -> Optional[str]:
        """
        Sanitize city name input.
        
        Args:
            city: City name to sanitize
            
        Returns:
            Sanitized city name or None if invalid
        """
        if not city:
            return None
            
        # Allow only letters, spaces, hyphens, and common punctuation
        sanitized = re.sub(r'[^\w\s\-.,]', '', city)
        
        # Limit length
        if len(sanitized) > 128:
            return None
            
        return sanitized.strip().title()
    
    @staticmethod
    def sanitize_tags(tags: Optional[str]) -> List[str]:
        """
        Sanitize and parse tags from comma-separated string.
        
        Args:
            tags: Comma-separated tags string
            
        Returns:
            List of sanitized tags
        """
        if not tags:
            return []
            
        # Split by comma
        tag_list = [tag.strip() for tag in tags.split(",") if tag.strip()]
        
        # Sanitize each tag
        sanitized_tags = []
        for tag in tag_list:
            # Allow only alphanumeric, spaces, hyphens, and underscores
            sanitized = re.sub(r'[^\w\s\-]', '', tag)
            if sanitized and len(sanitized) <= 50:
                sanitized_tags.append(sanitized.lower())
                
        return sanitized_tags
    
    @staticmethod
    def validate_property_type(property_type: Optional[str]) -> bool:
        """
        Validate property type against allowed values.
        
        Args:
            property_type: Property type to validate
            
        Returns:
            True if property type is valid, False otherwise
        """
        if not property_type:
            return True  # None is valid (optional filter)
            
        allowed_types = {
            'house', 'apartment', 'land', 'commercial', 
            'warehouse', 'office', 'villa', 'condominium'
        }
        
        return property_type.lower() in allowed_types
    
    @staticmethod
    def validate_source(source: Optional[str]) -> bool:
        """
        Validate data source against allowed values.
        
        Args:
            source: Source to validate
            
        Returns:
            True if source is valid, False otherwise
        """
        if not source:
            return True  # None is valid (optional filter)
            
        allowed_sources = {'olx', 'rumah123'}
        
        return source.lower() in allowed_sources
    
    @staticmethod
    def sanitize_price(price: Optional[int]) -> Optional[int]:
        """
        Validate and sanitize price input.
        
        Args:
            price: Price value to validate
            
        Returns:
            Sanitized price or None if invalid
        """
        if price is None:
            return None
            
        if not isinstance(price, int):
            return None
            
        # Price should be positive and within reasonable bounds
        if price < 0 or price > 10_000_000_000:  # Max 10 billion IDR
            return None
            
        return price