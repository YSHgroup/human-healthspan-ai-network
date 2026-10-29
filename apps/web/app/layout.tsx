import React from "react";
import type { Metadata, Viewport } from "next";
import "./globals.css";
import { Geist } from "next/font/google";
import { cn } from "@/lib/utils";
import { SessionProvider } from "@/lib/session";

const geist = Geist({ subsets: ["latin"], variable: "--font-geist-sans" });

const siteUrl = process.env.NEXT_PUBLIC_SITE_URL ?? "http://localhost:3000";
const description =
  "A global network for better human health, capability and longevity: people, researchers, clinicians and AI, working from evidence.";

export const metadata: Metadata = {
  metadataBase: new URL(siteUrl),
  title: {
    default: "Healthspan Network",
    template: "%s | Healthspan Network",
  },
  description,
  applicationName: "Healthspan Network",
  openGraph: {
    title: "Healthspan Network",
    description: "Better People. Better Science. A Healthier Future.",
    siteName: "Healthspan Network",
    type: "website",
    images: [
      {
        url: "/brand/ysh-nexus-banner.png",
        width: 2172,
        height: 724,
        alt: "YSH IT Nexus, a community for better health and better research",
      },
    ],
  },
  twitter: {
    card: "summary_large_image",
    title: "Healthspan Network",
    description: "Better People. Better Science. A Healthier Future.",
    images: ["/brand/ysh-nexus-banner.png"],
  },
};

export const viewport: Viewport = {
  themeColor: "#0a2a5e",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={cn("font-sans", geist.variable)}>
      <body><SessionProvider>{children}</SessionProvider></body>
    </html>
  );
}
