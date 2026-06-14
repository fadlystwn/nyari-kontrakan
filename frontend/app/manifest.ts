import type { MetadataRoute } from "next";

export const dynamic = "force-static";

export default function manifest(): MetadataRoute.Manifest {
  return {
    name: "NyariKontrakan - Cari Kontrakan Petakan",
    short_name: "NyariKontrakan",
    description: "Cari kontrakan Petakan terjangkau, strategis, dan lengkap di Jabodetabek.",
    start_url: "/",
    display: "standalone",
    background_color: "#FFFBFE",
    theme_color: "#6750A4",
    icons: [
      {
        src: "/favicon.ico",
        sizes: "any",
        type: "image/x-icon",
      },
    ],
  };
}
