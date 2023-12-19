#/bin/bash

# Update Repo
git pull &&

# Build Image
pack build --builder gcr.io/buildpacks/builder:v1 --path . deepcare-image &&

# Push to GCR
gcloud auth configure-docker &&
docker tag deepcare_image:latest gcr.io/deep-care-capstone/deepcare-image:latest &&
docker push gcr.io/deep-care-capstone/deepcare-image:latest &&

# Deploy to CloudRun
gcloud run deploy deepcare-service --image gcr.io/deep-care-capstone/deepcare-image:latest