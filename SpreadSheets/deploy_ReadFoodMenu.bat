cd /d %~dp0\ReadFoodMenu
gcloud functions deploy ReadFoodMenu --runtime nodejs8 --trigger-http --entry-point handler --region asia-northeast1