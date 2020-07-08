cd /d %~dp0\CW_nnc
gcloud functions deploy CW_nnc --runtime python37 --trigger-http --region asia-northeast1 --memory 512MB