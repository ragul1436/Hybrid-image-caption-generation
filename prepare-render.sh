#!/bin/bash

# Quick Render Deployment Script
# This script automates the setup for Render deployment

set -e

echo "🚀 Preparing for Render Deployment"
echo "=================================="
echo

# Check if Git is initialized
if [ ! -d ".git" ]; then
    echo "❌ Git repository not found!"
    echo "   Initialize with: git init"
    exit 1
fi

# Check if render.yaml exists
if [ ! -f "render.yaml" ]; then
    echo "❌ render.yaml not found!"
    echo "   Make sure render.yaml is in the project root"
    exit 1
fi

echo "✅ Git repository found"
echo "✅ render.yaml found"
echo

# Verify Render account
echo "📝 Before deploying, make sure you:"
echo "   1. Have a Render account (https://render.com)"
echo "   2. Have your GitHub repository connected"
echo "   3. Have generated strong secrets:"
echo

echo "      Generate SECRET_KEY:"
python3 -c "import secrets; print('      SECRET_KEY=' + secrets.token_urlsafe(32))"
echo

echo "   4. Updated render.yaml with your GitHub repo URL"
echo "   5. Updated BACKEND_CORS_ORIGINS to your domain(s)"
echo

# Check render.yaml configuration
if grep -q "YOUR_USERNAME" render.yaml; then
    echo "⚠️  ERROR: render.yaml contains placeholder YOUR_USERNAME"
    echo "   Update the 'repo' field with your actual GitHub repository"
    exit 1
fi

echo "✅ render.yaml looks good"
echo

# Verify requirements.txt exists
if [ ! -f "backend/requirements.txt" ]; then
    echo "❌ backend/requirements.txt not found!"
    exit 1
fi

echo "✅ backend/requirements.txt found"
echo

# Verify main.py exists
if [ ! -f "backend/app/main.py" ]; then
    echo "❌ backend/app/main.py not found!"
    exit 1
fi

echo "✅ backend/app/main.py found"
echo

# Git push
echo "📤 Preparing to push code to GitHub..."
git status

echo
read -p "Continue with git push? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    git push origin main
    echo "✅ Code pushed to GitHub"
else
    echo "⏭️  Skipped git push"
fi

echo
echo "✨ Render deployment ready!"
echo
echo "📝 Next steps:"
echo "   1. Go to https://dashboard.render.com"
echo "   2. Click 'New +' → 'Infrastructure as Code'"
echo "   3. Select your GitHub repository"
echo "   4. Click 'Deploy from render.yaml'"
echo
echo "   OR manually:"
echo "   1. Create PostgreSQL database first"
echo "   2. Create Web Service and link the database"
echo "   3. Set environment variables"
echo
echo "📚 Guide: RENDER_DEPLOYMENT.md"
echo
