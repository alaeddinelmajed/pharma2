#!/usr/bin/env bash
set -e

# Configuration
PROJECT_ID=${GCP_PROJECT_ID:-"pharma-ai-sovereign"}
REGION=${GCP_REGION:-"me-central1"}
SERVICE_NAME="pharma-procure-agent"

echo "🚀 Initiating Automated Cloud Build & Deployment to Google Cloud Run..."

# Build Container via Cloud Build
gcloud builds submit --tag gcr.io/$PROJECT_ID/$SERVICE_NAME . --project $PROJECT_ID

# Deploy to Cloud Run
gcloud run deploy $SERVICE_NAME \
    --image gcr.io/$PROJECT_ID/$SERVICE_NAME \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --port 8080 \
    --set-env-vars ENV=production,SOVEREIGN_CLOUD_PROVIDER=HUMAIN_KSA \
    --project $PROJECT_ID

echo "✅ Service successfully deployed!"
echo "🌐 Public URL:"
gcloud run services describe $SERVICE_NAME --platform managed --region $REGION --project $PROJECT_ID --format 'value(status.url)'
