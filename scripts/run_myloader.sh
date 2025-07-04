#!/bin/bash
set -e

GCS_BUCKET=$1
GCS_PATH=$2
TARGET_DB_HOST=$3
TARGET_DB_USER=$4
TARGET_DB_PASSWORD_SECRET=$5 # Secret name in Secret Manager
PROJECT_ID=$6

LOCAL_DUMP_DIR="/tmp/mydumper_data"
mkdir -p "${LOCAL_DUMP_DIR}"

echo "Downloading dump files from GCS..."
gsutil -m cp -r "gs://${GCS_BUCKET}/${GCS_PATH}/*" "${LOCAL_DUMP_DIR}/"

echo "Fetching target DB password from Secret Manager..."
TARGET_DB_PASS=$(gcloud secrets versions access latest --secret="${TARGET_DB_PASSWORD_SECRET}" --project="${PROJECT_ID}")

echo "Starting myloader import..."
myloader \
    --host="${TARGET_DB_HOST}" \
    --user="${TARGET_DB_USER}" \
    --password="${TARGET_DB_PASS}" \
    --directory="${LOCAL_DUMP_DIR}" \
    --threads=16 \
    --compress-protocol \
    --overwrite-tables \
    --verbose=3

echo "Myloader import finished."
rm -rf "${LOCAL_DUMP_DIR}"