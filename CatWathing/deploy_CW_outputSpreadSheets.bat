cd /d %~dp0\CW_outputSpreadSheets
gcloud functions deploy CW_outputSpreadSheets --runtime nodejs8 --trigger-http --entry-point handler --region asia-northeast1