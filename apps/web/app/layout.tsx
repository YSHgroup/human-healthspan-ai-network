import React from "react";

export const metadata = {
  title: "Human Healthspan Network",
  description: "Health, science, research and AI network",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return <html lang="en"><body>{children}</body></html>;
}
