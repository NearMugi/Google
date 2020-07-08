# deploy

gcloud functions deploy Drive_Upload\
 --runtime nodejs8 \
 --trigger-http \
 --entry-point handler \
 --region asia-northeast1 \
 --set-env-vars=DISABLE_LEGACY_METADATA_SERVER_ENDPOINTS=true \
 --allow-unauthenticated
