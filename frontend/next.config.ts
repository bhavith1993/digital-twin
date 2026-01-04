import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: 'export',
  images: {
    unoptimized: true
  },
  // Disable source maps in production for faster builds
  productionBrowserSourceMaps: false,
};

export default nextConfig;