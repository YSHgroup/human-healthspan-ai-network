import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Researcher Portal | Healthspan Network",
  description: "A foundation for protected scientific collaboration.",
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
