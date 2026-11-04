import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Researcher Portal | Healthspan Network",
  description: "A foundation for protected scientific collaboration.",
  robots: { index: false, follow: false },
  icons: {
    icon: "/brand/mark.png",
  },
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
