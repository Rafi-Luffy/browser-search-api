import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "CRW Browser API Playground",
  description: "Local API playground for the Kerala Ayurveda Browser API.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
