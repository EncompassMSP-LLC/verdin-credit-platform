import type { NextConfig } from 'next';

const nextConfig: NextConfig = {
  reactStrictMode: true,
  poweredByHeader: false,
  transpilePackages: ['@verdin/api-client', '@verdin/shared'],
};

export default nextConfig;
