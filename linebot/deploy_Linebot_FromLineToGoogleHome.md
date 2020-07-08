# deploy

gcloud functions deploy Linebot_FromLineToGoogleHome\
 --runtime nodejs8 \
 --trigger-http \
 --entry-point handler_Fromline \
 --region asia-northeast1 \
 --set-env-vars=DISABLE_LEGACY_METADATA_SERVER_ENDPOINTS=true \
 --allow-unauthenticated
