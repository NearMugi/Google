# deploy

gcloud functions deploy linebotSendImage\
 --runtime python37 \
 --trigger-http \
 --region asia-northeast1 \
 --set-env-vars=DISABLE_LEGACY_METADATA_SERVER_ENDPOINTS=true \
 --allow-unauthenticated
