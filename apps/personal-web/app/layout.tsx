import type { Metadata } from "next";
import { DM_Sans, DM_Serif_Display } from "next/font/google";

import "./globals.css";
import { ThemeProvider } from "@healthspan/ui/theme-provider";
import { Toaster } from "@healthspan/ui/sonner";

import { PortalShell } from "../components/portal/portal-shell";

const sans = DM_Sans({
  subsets: ["latin"],
  variable: "--font-healthspan-sans",
  display: "swap",
});
const display = DM_Serif_Display({
  subsets: ["latin"],
  weight: "400",
  variable: "--font-healthspan-display",
  display: "swap",
});

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
  // Sibling portal addresses are read on the server so the client shell can link to them.
  const urls = {
    social: process.env.PUBLIC_APP_URL ?? "http://localhost:3000",
    researcher: process.env.RESEARCHER_APP_URL ?? "http://localhost:3002",
  };
  const apiBaseUrl = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

  return (
    <html lang="en" data-portal="personal" suppressHydrationWarning>
      <body className={`${sans.variable} ${display.variable}`}>
        <ThemeProvider>
          <PortalShell urls={urls} apiBaseUrl={apiBaseUrl}>
            {children}
          </PortalShell>
          <Toaster />
        </ThemeProvider>
      </body>
    </html>
  );
}
