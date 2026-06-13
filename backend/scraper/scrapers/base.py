from abc import ABC, abstractmethod
from typing import List, Dict, Any

class BaseScraper(ABC):
    source: str  # must be set in subclass, e.g. "olx", "rumah123"

    @abstractmethod
    async def fetch_listings(self) -> List[Dict[str, Any]]:
        """
        Fetch listings from the source.
        Should return a list of raw listing dictionaries.
        Each dictionary must include at least:
          - external_id: unique ID from the source site
          - title: raw listing title
          - url: complete detail page URL
        """
        pass

    @abstractmethod
    def parse_listing(self, raw: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize a raw listing dictionary into the database schema format.
        Should return a dictionary containing the schema fields:
          - source
          - external_id
          - title
          - price (BIGINT or None)
          - location (TEXT or None)
          - city (VARCHAR or None)
          - property_type (VARCHAR or None)
          - bedrooms (INTEGER or None)
          - bathrooms (INTEGER or None)
          - land_area_sqm (INTEGER or None)
          - building_area_sqm (INTEGER or None)
          - url
          - photos (List[str])
          - raw_data (Dict[str, Any])
        """
        pass
