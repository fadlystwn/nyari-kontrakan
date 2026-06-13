import re
from typing import Optional

class Price:
    def __init__(self, value: Optional[int]):
        self.value = value

    @classmethod
    def parse(cls, price_text: str) -> "Price":
        if not price_text:
            return cls(None)
        
        text = price_text.lower().strip()
        
        # Check for Indonesian number scales
        multiplier = 1
        if "juta" in text:
            multiplier = 1_000_000
        elif "miliar" in text or "milyar" in text:
            multiplier = 1_000_000_000
            
        # Clean Rp, spaces, and non-numeric characters (except decimals)
        cleaned = re.sub(r"[^\d,\.]", "", text)
        
        # Handle cases with juta/miliar where we might have decimals like "Rp 1.5 Juta"
        if multiplier > 1:
            # Replace comma with dot for decimal parsing
            cleaned = cleaned.replace(",", ".")
            # If multiple dots exist (e.g. 1.500.000), keep only the last one or remove them
            if cleaned.count(".") > 1:
                # Standard formatting mistake with dots, just strip dots
                cleaned = cleaned.replace(".", "")
            try:
                val = float(cleaned) * multiplier
                return cls(int(val))
            except ValueError:
                pass
        
        # For standard format like Rp 1.500.000, remove all non-digits and parse
        cleaned_digits = re.sub(r"\D", "", text)
        if cleaned_digits:
            try:
                return cls(int(cleaned_digits))
            except ValueError:
                pass
                
        return cls(None)


class Location:
    def __init__(self, raw_address: str, city: Optional[str]):
        self.raw_address = raw_address
        self.city = city

    @classmethod
    def parse(cls, location_text: str) -> "Location":
        if not location_text:
            return cls("", None)
            
        parts = [p.strip() for p in location_text.split(",") if p.strip()]
        if not parts:
            return cls("", None)
            
        # Determine city from parts
        city = None
        if len(parts) >= 2:
            city = parts[-1]
            if city.lower() in ["dki jakarta", "jakarta", "banten", "jawa barat", "jawa tengah", "jawa timur"]:
                city = parts[-2]
        elif len(parts) == 1:
            city = parts[0]
            
        return cls(location_text, city)
