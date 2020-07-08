cd /d %~dp0\GPSMap_getMapBinary
gcloud functions deploy GPSMap_getMapBinary --runtime python37 --trigger-http --region asia-northeast1