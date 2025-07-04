#!/bin/bash
set -e

PROJECT_ID=$1
REGION=$2
SOURCE_PROFILE_NAME=$3
DESTINATION_SQL_ID=$4
MIGRATION_JOB_NAME="dms-job-$(date +%s)"

echo "Creating DMS migration job: ${MIGRATION_JOB_NAME}"

gcloud database-migration migration-jobs create "${MIGRATION_JOB_NAME}" \
    --project="${PROJECT_ID}" \
    --region="${REGION}" \
    --source="${SOURCE_PROFILE_NAME}" \
    --destination="${DESTINATION_SQL_ID}" \
    --display-name="${MIGRATION_JOB_NAME}" \
    --type=CONTINUOUS

echo "Starting DMS migration job..."
gcloud database-migration migration-jobs start "${MIGRATION_JOB_NAME}" \
    --project="${PROJECT_ID}" \
    --region="${REGION}"

echo "DMS job started. Monitor progress in the GCP console."