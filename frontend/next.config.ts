import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  async rewrites() {
    // Only rewrite API routes in development
    // In production, Vercel will handle the routing
    if (process.env.NODE_ENV === 'development') {
      return [
        {
          source: '/api/:path*',
          destination: 'http://localhost:8000/:path*',
        },
      ];
    }
    return [];
  },
};

export default nextConfig;
