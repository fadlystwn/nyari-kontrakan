import { Property, mockProperties } from '../data/properties';
import { DEFAULT_FACILITIES, API_LIMIT, DEFAULT_API_URL } from '../constants';

interface BackendListing {
  id: string | number;
  title: string;
  location?: string;
  city?: string;
  price?: number;
  tags?: string[];
  photos?: string[];
}

/**
 * Fetches listings from the backend API and maps them to Property objects.
 * Falls back to mockProperties if backend returns empty/no results.
 */
export const getProperties = async (): Promise<Property[]> => {
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || DEFAULT_API_URL;
  const res = await fetch(`${apiUrl}/listings?limit=${API_LIMIT}`);
  
  if (!res.ok) {
    throw new Error(`HTTP error! status: ${res.status}`);
  }
  
  const data = await res.json();
  
  if (data && data.listings && data.listings.length > 0) {
    return data.listings.map((listing: BackendListing) => ({
      id: `backend-${listing.id}`,
      name: listing.title,
      location: listing.location || `${listing.city || 'Jabodetabek'}`,
      city: listing.city || 'Lainnya',
      pricePerMonth: listing.price || 0,
      facilities: listing.tags && listing.tags.length > 0 ? listing.tags : DEFAULT_FACILITIES,
      imageUrl: listing.photos && listing.photos.length > 0 ? listing.photos[0] : `https://picsum.photos/800/600?random=${listing.id}`,
      available: true,
      petakCount: 3,
    }));
  }
  
  return mockProperties;
};
