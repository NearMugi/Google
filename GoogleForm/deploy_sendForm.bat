cd /d %~dp0\sendForm
gcloud functions deploy googleFormSend --runtime python37 --trigger-http --region asia-northeast1 --memory 512MB