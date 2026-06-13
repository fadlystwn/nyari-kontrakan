import type { MetadataRoute } from "next";

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const siteUrl = process.env.NEXT_PUBLIC_SITE_URL || "https://nyarikontrakan.com";

  // Base routes
  const routes = [
    {
      url: siteUrl,
      lastModified: new Date(),
      changeFrequency: "daily" as const,
      priority: 1.0,
    },
  ];

  // If there are dynamic detail routes in the future, we would fetch them here:
  /*
  try {
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
    const res = await fetch(`${apiUrl}/listings?limit=100`, { next: { revalidate: 3600 } });
    if (res.ok) {
      const data = await res.json();
      const listings = data.listings || [];
      const listingRoutes = listings.map((listing: any) => ({
        url: `${siteUrl}/listings/${listing.id}`,
        lastModified: new Date(listing.updated_at || new Date()),
        changeFrequency: "weekly" as const,
        priority: 0.8,
      }));
      return [...routes, ...listingRoutes];
    }
  } catch (error) {
    console.error("Error fetching listings for sitemap:", error);
  }
  */

  return routes;
}
