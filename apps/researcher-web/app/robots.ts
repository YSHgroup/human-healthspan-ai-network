import type { MetadataRoute } from "next";

// This portal contains private or access-controlled content and must never be indexed.
export default function robots(): MetadataRoute.Robots {
  return {
    rules: {
      userAgent: "*",
      disallow: "/",
    },
  };
}
