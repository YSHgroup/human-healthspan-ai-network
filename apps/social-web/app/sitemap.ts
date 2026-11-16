import type { MetadataRoute } from "next";

export default function sitemap(): MetadataRoute.Sitemap {
  const siteUrl = process.env.PUBLIC_APP_URL ?? "http://localhost:3000";

  return [
    {
      url: siteUrl,
      changeFrequency: "monthly",
      priority: 1,
    },
    {
      url: `${siteUrl}/feed`,
      changeFrequency: "daily",
      priority: 0.8,
    },
  ];
}
