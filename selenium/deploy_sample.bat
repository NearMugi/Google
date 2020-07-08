cd /d %~dp0\sample
gcloud functions deploy seleniumSample --runtime python37 --trigger-http --region asia-northeast1 --memory 512MB