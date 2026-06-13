import type { Metadata } from "next";
import { Roboto } from "next/font/google";
import ThemeRegistry from "../theme/ThemeRegistry";
import "./globals.css";

const roboto = Roboto({
  weight: ["300", "400", "500", "700"],
  subsets: ["latin"],
  display: "swap",
  variable: "--font-roboto",
});

export const metadata: Metadata = {
  metadataBase: new URL(process.env.NEXT_PUBLIC_SITE_URL || "https://nyarikontrakan.com"),
  title: {
    default: "NyariKontrakan - Cari Kontrakan Petakan Terjangkau",
    template: "%s | NyariKontrakan"
  },
  description: "Cari kontrakan Petakan dengan harga terjangkau, lokasi strategis, dan fasilitas lengkap. Temukan kontrakan impian Anda di Jabodetabek.",
  keywords: ["kontrakan", "sewa kontrakan", "kontrakan petakan", "sewa rumah petak", "kontrakan murah", "kontrakan bekasi", "kontrakan tangerang", "kontrakan depok", "kontrakan jakarta"],
  authors: [{ name: "NyariKontrakan Team" }],
  creator: "NyariKontrakan",
  publisher: "NyariKontrakan",
  formatDetection: {
    email: false,
    address: true,
    telephone: true,
  },
  alternates: {
    canonical: "/",
  },
  openGraph: {
    title: "NyariKontrakan - Cari Kontrakan Petakan Terjangkau",
    description: "Cari kontrakan Petakan dengan harga terjangkau, lokasi strategis, dan fasilitas lengkap. Temukan kontrakan impian Anda di Jabodetabek.",
    url: "https://nyarikontrakan.com",
    siteName: "NyariKontrakan",
    locale: "id_ID",
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: "NyariKontrakan - Cari Kontrakan Petakan Terjangkau",
    description: "Cari kontrakan Petakan dengan harga terjangkau, lokasi strategis, dan fasilitas lengkap. Temukan kontrakan impian Anda di Jabodetabek.",
    creator: "@nyarikontrakan",
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      "max-video-preview": -1,
      "max-image-preview": "large",
      "max-snippet": -1,
    },
  },
};

export const viewport = {
  themeColor: "#6750A4",
  width: "device-width",
  initialScale: 1,
};


export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="id" className={roboto.variable}>
      <body>
        <ThemeRegistry>
          {children}
        </ThemeRegistry>
      </body>
    </html>
  );
}
