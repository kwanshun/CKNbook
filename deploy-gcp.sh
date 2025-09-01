#!/bin/bash

# Google Cloud Platform Deployment Script for Tone-Toner

echo "🚀 Deploying Tone-Toner to Google Cloud Platform..."

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "❌ Google Cloud SDK not found. Please install it first:"
    echo "   https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Set variables
PROJECT_ID=""
REGION="us-central1"
SERVICE_NAME="tone-toner"

# Get project ID if not set
if [ -z "$PROJECT_ID" ]; then
    echo "📝 Please enter your Google Cloud Project ID:"
    read -r PROJECT_ID
fi

# Set the project
echo "🔧 Setting project to $PROJECT_ID..."
gcloud config set project $PROJECT_ID

# Enable required APIs
echo "🔌 Enabling required Google Cloud APIs..."
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com

# Get API keys
echo "🔑 Please enter your Gemini API key:"
read -s GEMINI_API_KEY

echo "🔑 Please enter a secret key for Flask (64+ characters):"
read -s FLASK_SECRET_KEY

# Build and deploy using Cloud Build
echo "🏗️  Building and deploying with Cloud Build..."
gcloud builds submit \
    --config cloudbuild.yaml \
    --substitutions _API_KEY="$GEMINI_API_KEY",_SECRET_KEY="$FLASK_SECRET_KEY"

# Get the service URL
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region=$REGION --format="value(status.url)")

echo "✅ Deployment complete!"
echo "🌐 Your Tone-Toner app is available at: $SERVICE_URL"
echo ""
echo "📋 Next steps:"
echo "   1. Test your app at the URL above"
echo "   2. Configure custom domain (optional)"
echo "   3. Set up monitoring and logging"

