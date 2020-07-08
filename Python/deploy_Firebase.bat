cd /d %~dp0\Firebase
gcloud functions deploy FirebaseSample --runtime python37 --trigger-http --region asia-northeast1