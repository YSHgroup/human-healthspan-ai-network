import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Healthspan Network Admin",
  robots: { index: false, follow: false, noarchive: true },
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en" translate="no">
      <body>{children}</body>
    </html>
  );
}
