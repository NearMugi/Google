cd /d %~dp0\CreateImgWeather
gcloud functions deploy CreateImgWeather --runtime python37 --trigger-resource CreateImgWeather  --env-vars-file .env.yaml --trigger-event google.pubsub.topic.publish --region asia-northeast1