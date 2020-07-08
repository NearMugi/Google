cd /d %~dp0\WriteCatWatching
gcloud functions deploy WriteCatWatching --runtime nodejs8 --trigger-http --entry-point handler --region asia-northeast1