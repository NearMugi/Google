cd /d %~dp0\helloWorld
gcloud functions deploy helloWorld --runtime python37 --trigger-http --region asia-northeast1