/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'export',  // 啟用靜態導出
  basePath: '/rental-website',  // GitHub Pages 子路徑
  images: {
    unoptimized: true  // GitHub Pages 不支援 Image Optimization
  },
  env: {
    NEXT_PUBLIC_BASE_PATH: '/rental-website'
  }
}

module.exports = nextConfig
