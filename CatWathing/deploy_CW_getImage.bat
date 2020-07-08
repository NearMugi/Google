cd /d %~dp0\CW_getImage
gcloud functions deploy CW_getImage --runtime python37 --trigger-http --region asia-northeast1