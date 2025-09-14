/** @type {import('next').NextConfig} */
const nextConfig = {
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'http://localhost:8000/api/:path*',
      },
      {
        source: '/data/:path*',
        destination: '/data_agent/output/:path*',
      },
    ]
  },
}

module.exports = nextConfig
