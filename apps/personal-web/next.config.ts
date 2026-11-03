import type { NextConfig } from "next";

// Workspace packages are consumed as TypeScript source.
const nextConfig: NextConfig = {
  transpilePackages: ["@healthspan/ui", "@healthspan/api-client", "@healthspan/auth-client", "@healthspan/shared-types", "@healthspan/shared-config", "@healthspan/validation", "@healthspan/design-tokens"],
};
export default nextConfig;
