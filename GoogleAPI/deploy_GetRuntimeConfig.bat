cd /d %~dp0\GetRuntimeConfig
gcloud functions deploy GetRuntimeConfig --runtime nodejs8 --trigger-http --entry-point handler --region asia-northeast1