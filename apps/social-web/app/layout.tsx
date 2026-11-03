import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  metadataBase: new URL(process.env.PUBLIC_APP_URL ?? "http://localhost:3000"),
  title: {
    default: "Human Healthspan Scientific AI Network",
    template: "%s | Healthspan Network",
  },
  description:
    "A global network connecting people, scientific communities, research, and responsible AI to improve human healthspan.",
  applicationName: "Human Healthspan Scientific AI Network",
  alternates: {
    canonical: "/",
  },
  icons: {
    icon: "/brand/mark.png",
  },
  openGraph: {
    title: "Human Healthspan Scientific AI Network",
    description:
      "Better health through open community, rigorous research, and responsible scientific AI.",
    url: "/",
    type: "website",
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
