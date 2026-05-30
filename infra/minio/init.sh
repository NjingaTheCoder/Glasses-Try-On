#!/bin/sh
# MinIO initialization script
# Creates the required bucket for WearLens storage

set -e

echo "Waiting for MinIO to be ready..."
sleep 5

echo "Configuring MinIO client..."
mc alias set myminio http://minio:9000 ${MINIO_ROOT_USER} ${MINIO_ROOT_PASSWORD}

echo "Creating bucket: ${MINIO_BUCKET_NAME}"
mc mb myminio/${MINIO_BUCKET_NAME} --ignore-existing

echo "Setting bucket policy to allow downloads..."
mc anonymous set download myminio/${MINIO_BUCKET_NAME}

echo "MinIO initialization complete!"
