cd /d %~dp0\GetRuntimeConfig_python
gcloud functions deploy GetRuntimeConfig_python --runtime python37 --trigger-http --region asia-northeast1