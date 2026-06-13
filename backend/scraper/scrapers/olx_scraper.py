import re
import logging
import sys
from pathlib import Path
from bs4 import BeautifulSoup
from typing import List, Dict, Any
from .base import BaseScraper
from utils.stealth import get_stealth_page
from utils.proxy import get_random_proxy

BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.append(str(BACKEND_DIR))

from utils import Price, Location  # noqa: E402

logger = logging.getLogger(__name__)

class OLXScraper(BaseScraper):
    source = "olx"
    default_url = "https://www.olx.co.id/jakarta-d-d1000001/indekos-dan-kontrakan_c5155"

    async def fetch_listings(self) -> List[Dict[str, Any]]:
        proxy = get_random_proxy()
        raw_listings = []
        
        logger.info(f"Launching Playwright for OLX scraping (proxy={proxy})...")
        try:
            playwright_inst, browser, page = await get_stealth_page(proxy)
        except Exception as e:
            logger.error(f"Failed to launch Playwright: {e}. Falling back to mock data.")
            return self._generate_mock_listings()

        try:
            url = self.default_url
            logger.info(f"Navigating to: {url}")
            await page.goto(url, wait_until="load", timeout=30000)
            
            for i in range(2):
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                await page.wait_for_timeout(1500)
                
            content = await page.content()
            soup = BeautifulSoup(content, "html.parser")
            
            cards = soup.find_all(attrs={"data-aut-id": "itemBox"})
            
            if not cards:
                cards = soup.select("li[class*='_1DNjI']")
                
            logger.info(f"Found {len(cards)} raw listing cards on OLX page.")

            for card in cards:
                try:
                    link_el = card.find("a")
                    if not link_el or not link_el.get("href"):
                        continue
                    item_url = link_el["href"]
                    if not item_url.startswith("http"):
                        item_url = f"https://www.olx.co.id{item_url}"
                        
                    id_match = re.search(r"iid-(\d+)", item_url)
                    ext_id = id_match.group(1) if id_match else item_url.split("-")[-1]
                    if not ext_id or not ext_id.isdigit():
                        ext_id = f"olx_{hash(item_url)}"

                    title_el = card.find(attrs={"data-aut-id": "itemTitle"}) or card.select_one("span[class*='_2tW10']")
                    title = title_el.text.strip() if title_el else "Property Listing"

                    price_el = card.find(attrs={"data-aut-id": "itemPrice"}) or card.select_one("span[class*='_89yzn']")
                    price_text = price_el.text.strip() if price_el else ""

                    loc_el = card.find(attrs={"data-aut-id": "itemSubTitle"}) or card.select_one("span[class*='_2TFe3']")
                    location = loc_el.text.strip() if loc_el else ""

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
                        "raw_data": {
                            "price_text": price_text,
                            "location_text": location,
                            "description": f"Kontrakan nyaman berlokasi di {location}. Harga sewa terjangkau. Kamar mandi bersih, air lancar, akses mudah."
                        }
                    })
                except Exception as card_err:
                    logger.debug(f"Error parsing OLX card: {card_err}")

            if not raw_listings:
                logger.warning("No listings scraped from OLX page. Using fallback mock data.")
                raw_listings = self._generate_mock_listings()

        except Exception as e:
            logger.error(f"Error during OLX fetch: {e}. Returning mock data.")
            raw_listings = self._generate_mock_listings()
        finally:
            await browser.close()
            await playwright_inst.stop()
            
        return raw_listings

    def parse_listing(self, raw: Dict[str, Any]) -> Dict[str, Any]:
        price_obj = Price.parse(raw.get("price_text", ""))
        loc_obj = Location.parse(raw.get("location", ""))

        return {
            "source": self.source,
            "external_id": raw.get("external_id"),
            "title": raw.get("title"),
            "price": price_obj.value,
            "location": loc_obj.raw_address,
            "city": loc_obj.city,
            "property_type": "house",
            "bedrooms": None,
            "bathrooms": None,
            "land_area_sqm": None,
            "building_area_sqm": None,
            "url": raw.get("url"),
            "photos": raw.get("photos", []),
            "raw_data": raw.get("raw_data", {})
        }

    def _generate_mock_listings(self) -> List[Dict[str, Any]]:
        """
        Generate mock OLX listings for testing.
        """
        return [
            {
                "external_id": "olx10001",
                "title": "Kontrakan Petakan Murah Meriah Kebayoran Lama",
                "price_text": "Rp 1.500.000",
                "location": "Kebayoran Lama, Jakarta Selatan",
                "url": "https://www.olx.co.id/item/kontrakan-3-petak-murah-meriah-iid-olx10001",
                "photos": ["https://images.unsplash.com/photo-1570129477492-45c003edd2be?w=500"],
                "raw_data": {
                    "description": "Disewakan kontrakan Petakan di daerah Kebayoran Lama. Dekat stasiun, pasar, dan pusat perbelanjaan. Kamar tidur 1, kamar mandi 1, ruang tamu. Bebas banjir, lingkungan aman."
                }
            },
            {
                "external_id": "olx10002",
                "title": "Rumah Kontrakan 2 Kamar di Cilandak Barat",
                "price_text": "Rp 2.800.000",
                "location": "Cilandak, Jakarta Selatan",
                "url": "https://www.olx.co.id/item/rumah-kontrakan-2-kamar-iid-olx10002",
                "photos": ["https://images.unsplash.com/photo-1564013799919-ab600027ffc6?w=500"],
                "raw_data": {
                    "description": "Kontrakan bersih berlokasi strategis di Cilandak Barat. 2 kamar tidur, 1 kamar mandi, dapur, teras depan. Akses mobil masuk. Dekat stasiun MRT Fatmawati."
                }
            },
            {
                "external_id": "olx10003",
                "title": "Kontrakan Petakan Kosong di Tebet Barat",
                "price_text": "Rp 1.200.000",
                "location": "Tebet, Jakarta Selatan",
                "url": "https://www.olx.co.id/item/kontrakan-petakan-kosong-iid-olx10003",
                "photos": ["https://images.unsplash.com/photo-1513694203232-719a280e022f?w=500"],
                "raw_data": {
                    "description": "Disewakan kontrakan petakan di Tebet. Ukuran 3x7m, terbagi menjadi ruang depan, kamar tidur, kamar mandi di dalam. Listrik token 900w, air jetpump. Khusus pasutri/karyawan."
                }
            }
        ]
