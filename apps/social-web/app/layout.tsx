import type { Metadata } from "next";
import { DM_Sans, DM_Serif_Display } from "next/font/google";

import "./globals.css";
import { ThemeProvider } from "@healthspan/ui/theme-provider";
import { Toaster } from "@healthspan/ui/sonner";

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
    <html lang="en" data-portal="social" suppressHydrationWarning>
      <body className={`${sans.variable} ${display.variable}`}>
        <ThemeProvider>
          {children}
          <Toaster />
        </ThemeProvider>
      </body>
    </html>
  );
}
