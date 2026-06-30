import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Satellite Segmentation Demo",
  description: "Interactive portfolio demo for satellite image segmentation predictions.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
