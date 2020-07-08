cd /d %~dp0\imageResize
gcloud functions deploy imageResize --runtime python37 --trigger-http --region asia-northeast1