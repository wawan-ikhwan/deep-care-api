#/bin/bash

# # Build Image
# pack build deepcare_image --builder gcr.io/buildpacks/builder:v1 --path . &&

# # Push to GCR
# gcloud auth configure-docker &&
# docker tag deepcare_image:latest gcr.io/deep-care-capstone/deepcare_image:latest &&
# docker push gcr.io/deep-care-capstone/deepcare_image:latest &&

# # Deploy to CloudRun
# gcloud run deploy deepcare-api \
#   --image gcr.io/deep-care-capstone/deepcare_image:latest \
#   --region asia-southeast2 \
#   --allow-unauthenticated

# Trigger Cloud Build
gcloud builds submit --config cloudbuild.yaml

# Deploy to Cloud Run
gcloud run deploy deepcare-api \
  --image gcr.io/deep-care-capstone/deepcare_image:latest \
  --region asia-southeast2 \
  --allow-unauthenticated