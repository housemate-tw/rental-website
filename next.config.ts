import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Codex: 明確指定 Turbopack 根目錄，避免向上錯抓其他 lockfile
  turbopack: {
    root: __dirname,
  },
  output: 'export',
  basePath: '/rental-website',
  images: {
    unoptimized: true,
  },
  eslint: {
    ignoreDuringBuilds: true,
  },
  typescript: {
    ignoreBuildErrors: true,
  },
};

export default nextConfig;
