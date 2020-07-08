cd /d %~dp0\GetInfo
gcloud functions deploy Drive_GetInfo --trigger-http --entry-point handler --region asia-northeast1 --runtime nodejs8