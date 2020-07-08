# deploy

cd Google/linebot/Line_GoogleHome

gcloud functions deploy Linebot_FromGoogleHomeToLine\
 --runtime nodejs10 \
 --trigger-http \
 --entry-point handler_Toline \
 --region asia-northeast1 \
 --set-env-vars=DISABLE_LEGACY_METADATA_SERVER_ENDPOINTS=true \
 --allow-unauthenticated
