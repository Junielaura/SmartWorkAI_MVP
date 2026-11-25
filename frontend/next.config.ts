import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* config options here */
  skipTrailingSlashRedirect: true,
  async rewrites() {
    const apiUrl = process.env.API_INTERNAL_URL ?? "http://localhost:8100";
    return [
      {
        source: "/api/v1/:path*",
        destination: `${apiUrl}/api/v1/:path*`,
      },
    ];
  },
  turbopack: {
    rules: {
      "*.css": {
        loaders: ["@tailwindcss/turbopack"],
        as: "*.css",
      },
    },
  },
};

export default nextConfig;
