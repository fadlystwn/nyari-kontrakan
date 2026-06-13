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
  title: "NyariKontrakan - Cari Kontrakan Petakan Terjangkau",
  description: "Cari kontrakan Petakan dengan harga terjangkau, lokasi strategis, dan fasilitas lengkap. Temukan kontrakan impian Anda di Jabodetabek.",
  keywords: "kontrakan, sewa kontrakan, kontrakan Petakan, sewa rumah petak, kontrakan murah, kontrakan bekasi, kontrakan tangerang, kontrakan depok, kontrakan jakarta",
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
