import React from "react";
import type { Metadata, Viewport } from "next";
import "./globals.css";
import { Geist } from "next/font/google";
import { cn } from "@/lib/utils";
import { SessionProvider } from "@/lib/session";

const geist = Geist({ subsets: ["latin"], variable: "--font-geist-sans" });

export const metadata: Metadata = {
  title: { default: "Personal Space | Healthspan Network", template: "%s | Personal Space" },
  description: "Your identity, professional record, private health data and sharing controls.",
  applicationName: "Healthspan Network",
};

export const viewport: Viewport = { themeColor: "#0a2a5e" };

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={cn("font-sans", geist.variable)}>
      <body><SessionProvider>{children}</SessionProvider></body>
    </html>
  );
}
