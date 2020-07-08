cd /d %~dp0\GetAccessToken
gcloud functions deploy GetAccessToken --runtime nodejs8 --trigger-http --entry-point handler --region asia-northeast1