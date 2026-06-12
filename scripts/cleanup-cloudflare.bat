@echo off
REM Cleanup script for converting to Vercel deployment (Windows)

echo.
echo ===================================================
echo  Cloudflare to Vercel Migration Cleanup
echo ===================================================
echo.

echo 🧹 Cleaning up Cloudflare artifacts...
echo.

REM Remove Cloudflare directories and files
if exist frontend\.wrangler (
    echo Removing frontend\.wrangler directory...
    rmdir /s /q frontend\.wrangler
)

if exist frontend\wrangler.json (
    echo Removing frontend\wrangler.json...
    del frontend\wrangler.json
)

if exist frontend\wrangler.jsonc (
    echo Removing frontend\wrangler.jsonc...
    del frontend\wrangler.jsonc
)

if exist frontend\dist\client\wrangler.json (
    echo Removing frontend\dist\client\wrangler.json...
    del frontend\dist\client\wrangler.json
)

echo.
echo ✅ Cleanup complete!
echo.
echo 📦 Next steps:
echo    1. cd frontend
echo    2. npm install
echo    3. npm run build
echo    4. npm run preview
echo.
echo 🚀 To deploy to Vercel:
echo    1. Push your code to GitHub
echo    2. Go to https://vercel.com and import your repository
echo    3. Set environment variable VITE_BACKEND_URL in dashboard
echo    4. Deploy!
echo.
echo 📚 Read VERCEL_DEPLOYMENT.md for detailed instructions
echo.
pause
