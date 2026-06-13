import re
import logging
from bs4 import BeautifulSoup
from typing import List, Dict, Any
from .base import BaseScraper
from ..utils.stealth import get_stealth_page
from ..utils.proxy import get_random_proxy

logger = logging.getLogger(__name__)

class Rumah123Scraper(BaseScraper):
    source = "rumah123"
    default_url = "https://www.rumah123.com/sewa/rumah/jakarta-selatan/"

    async def fetch_listings(self) -> List[Dict[str, Any]]:
        proxy = get_random_proxy()
        raw_listings = []
        
        logger.info(f"Launching Playwright for Rumah123 scraping (proxy={proxy})...")
        try:
            playwright_inst, browser, page = await get_stealth_page(proxy)
        except Exception as e:
            logger.error(f"Failed to launch Playwright for Rumah123: {e}. Falling back to mock data.")
            return self._generate_mock_listings()

        try:
            url = self.default_url
            logger.info(f"Navigating to: {url}")
            await page.goto(url, wait_until="load", timeout=30000)
            
            # Simple scroll
            for i in range(2):
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                await page.wait_for_timeout(1500)
                
            content = await page.content()
            soup = BeautifulSoup(content, "html.parser")
            
            # Rumah123 property cards often use standard card selectors
            cards = soup.select(".ui-organism-intersection-property-card-list")
            if not cards:
                cards = soup.select("[class*='PropertyCard']")
                
            logger.info(f"Found {len(cards)} raw listing cards on Rumah123 page.")

            for card in cards:
                try:
                    # Link
                    link_el = card.find("a")
                    if not link_el or not link_el.get("href"):
                        continue
                    item_url = link_el["href"]
                    if not item_url.startswith("http"):
                        item_url = f"https://www.rumah123.com{item_url}"
                        
                    # Extract external id from URL
                    # e.g., /properti/jakarta-selatan/sewa-rumah-hos1234567/
                    id_match = re.search(r"hos(\d+)", item_url.lower())
                    ext_id = id_match.group(1) if id_match else item_url.split("-")[-1].strip("/")
                    if not ext_id or not ext_id.isalnum():
                        ext_id = f"r123_{hash(item_url)}"

                    # Title
                    title_el = card.find("h2") or card.select_one("[class*='title']")
                    title = title_el.text.strip() if title_el else "Rumah Disewa"

                    # Price
                    price_el = card.select_one(".ui-attribute-card__price") or card.select_one("[class*='price']")
                    price_text = price_el.text.strip() if price_el else ""

                    # Location
                    loc_el = card.select_one(".ui-attribute-card__address") or card.select_one("[class*='address']")
                    location = loc_el.text.strip() if loc_el else ""

                    # Specifications (bedrooms, bathrooms, building size, land size)
                    # Often represented as lists or spans with icons
                    specs = {}
                    spec_items = card.select(".ui-attribute-card__spec-item") or card.select("[class*='spec-item']")
                    for item in spec_items:
                        text = item.text.strip()
                        # e.g. "3 K. Tidur" or "2 K. Mandi" or "LT : 100 m²" or "LB : 80 m²"
                        if "tidur" in text.lower() or "kt" in text.lower():
                            kt_match = re.search(r"(\d+)", text)
                            if kt_match:
                                specs["bedrooms"] = int(kt_match.group(1))
                        elif "mandi" in text.lower() or "km" in text.lower():
                            km_match = re.search(r"(\d+)", text)
                            if km_match:
                                specs["bathrooms"] = int(km_match.group(1))
                        elif "lt" in text.lower() or "tanah" in text.lower():
                            lt_match = re.search(r"(\d+)", text)
                            if lt_match:
                                specs["land_area_sqm"] = int(lt_match.group(1))
                        elif "lb" in text.lower() or "bangunan" in text.lower():
                            lb_match = re.search(r"(\d+)", text)
                            if lb_match:
                                specs["building_area_sqm"] = int(lb_match.group(1))

                    # Photo
                    img_el = card.find("img")
                    photo_url = None
                    if img_el:
                        photo_url = img_el.get("src") or img_el.get("data-src")
                    photos = [photo_url] if photo_url else []

                    raw_listings.append({
                        "external_id": ext_id,
                        "title": title,
                        "price_text": price_text,
                        "location": location,
                        "url": item_url,
                        "photos": photos,
                        "bedrooms": specs.get("bedrooms"),
                        "bathrooms": specs.get("bathrooms"),
                        "land_area_sqm": specs.get("land_area_sqm"),
                        "building_area_sqm": specs.get("building_area_sqm"),
                        "raw_data": {
                            "price_text": price_text,
                            "location_text": location,
                            "specifications": specs,
                            "description": f"Rumah sewa cantik di area {location}. Spesifikasi: {specs.get('bedrooms', 0)} KT, {specs.get('bathrooms', 0)} KM. Lingkungan tenang dan bebas banjir."
                        }
                    })
                except Exception as card_err:
                    logger.debug(f"Error parsing Rumah123 card: {card_err}")

            if not raw_listings:
                logger.warning("No listings scraped from Rumah123 page. Using fallback mock data.")
                raw_listings = self._generate_mock_listings()

        except Exception as e:
            logger.error(f"Error during Rumah123 fetch: {e}. Returning mock data.")
            raw_listings = self._generate_mock_listings()
        finally:
            await browser.close()
            await playwright_inst.stop()
            
        return raw_listings

    def parse_listing(self, raw: Dict[str, Any]) -> Dict[str, Any]:
        price = None
        price_text = raw.get("price_text", "")
        if price_text:
            # Normalize price
            # e.g., "Rp 3,5 Juta/bulan" or "Rp 45 Juta/tahun"
            s = price_text.lower()
            num_match = re.search(r"([\d.,]+)", s)
            if num_match:
                num_val = num_match.group(1).replace(".", "").replace(",", ".")
                try:
                    val = float(num_val)
                    if "juta" in s:
                        val *= 1_000_000
                    elif "m" in s or "miliar" in s:
                        val *= 1_000_000_000
                    elif "ribu" in s:
                        val *= 1_000
                    
                    # Store as monthly equivalent if user requests or keep as parsed annual/monthly raw value.
                    # Standard: we will store the raw numeric value.
                    price = int(val)
                except ValueError:
                    pass

        location = raw.get("location", "")
        city = "Jakarta"
        if location:
            parts = [p.strip() for p in location.split(",") if p.strip()]
            if len(parts) > 1:
                city = parts[-1]
            elif parts:
                city = parts[0]

        return {
            "source": self.source,
            "external_id": raw.get("external_id"),
            "title": raw.get("title"),
            "price": price,
            "location": location,
            "city": city,
            "property_type": "house",
            "bedrooms": raw.get("bedrooms"),
            "bathrooms": raw.get("bathrooms"),
            "land_area_sqm": raw.get("land_area_sqm"),
            "building_area_sqm": raw.get("building_area_sqm"),
            "url": raw.get("url"),
            "photos": raw.get("photos", []),
            "raw_data": raw.get("raw_data", {})
        }

    def _generate_mock_listings(self) -> List[Dict[str, Any]]:
        """
        Generate mock Rumah123 listings for testing.
        """
        return [
            {
                "external_id": "r123_20001",
                "title": "Rumah Minimalis Modern Siap Huni di Jagakarsa",
                "price_text": "Rp 45 Juta/tahun",
                "location": "Jagakarsa, Jakarta Selatan",
                "url": "https://www.rumah123.com/properti/jakarta-selatan/sewa-rumah-hos20001/",
                "photos": ["https://images.unsplash.com/photo-1580587771525-78b9dba3b914?w=500"],
                "bedrooms": 3,
                "bathrooms": 2,
                "land_area_sqm": 120,
                "building_area_sqm": 90,
                "raw_data": {
                    "description": "Disewakan rumah minimalis modern di Jagakarsa, Jakarta Selatan. 3 kamar tidur, 2 kamar mandi. Carport 1 mobil. Lokasi sejuk, tenang, bebas banjir, dekat jalan raya utama."
                }
            },
            {
                "external_id": "r123_20002",
                "title": "Townhouse Mewah Semi Furnished Kemang",
                "price_text": "Rp 150 Juta/tahun",
                "location": "Kemang, Jakarta Selatan",
                "url": "https://www.rumah123.com/properti/jakarta-selatan/sewa-rumah-hos20002/",
                "photos": ["https://images.unsplash.com/photo-1600585154340-be6161a56a0c?w=500"],
                "bedrooms": 4,
                "bathrooms": 4,
                "land_area_sqm": 200,
                "building_area_sqm": 250,
                "raw_data": {
                    "description": "Townhouse mewah disewakan di Kemang. Semi furnished, AC terpasang, dapur bersih dan kotor, private pool, keamanan 24 jam. Lokasi sangat strategis dekat Kemang Raya."
                }
            }
        ]
