cd /d %~dp0\ReadAndWriteWakeup
gcloud functions deploy ReadAndWriteWakeup --runtime nodejs8 --trigger-http --entry-point handler --region asia-northeast1