#!/bin/bash
# Cleanup script for converting to Vercel deployment

echo "🧹 Cleaning up Cloudflare artifacts..."

# Remove Cloudflare directories
rm -rf frontend/.wrangler
rm -f frontend/wrangler.json
rm -f frontend/wrangler.jsonc
rm -f frontend/dist/client/wrangler.json

# Remove Bun lock file if it exists (we'll use npm)
# Uncomment if you want to switch from Bun to npm:
# rm -f frontend/bun.lock

echo "✅ Cleanup complete!"
echo ""
echo "📦 Next steps:"
echo "1. cd frontend"
echo "2. npm install  # or bun install if you prefer Bun"
echo "3. npm run build"
echo "4. npm run preview"
echo ""
echo "🚀 To deploy to Vercel:"
echo "1. Push your code to GitHub"
echo "2. Go to https://vercel.com and import your repository"
echo "3. Set environment variable VITE_BACKEND_URL to your backend API URL"
echo "4. Deploy!"
