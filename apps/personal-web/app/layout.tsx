import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Personal Portal | Healthspan Network",
  description: "Your personal profile and interests in the Healthspan Network.",
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
