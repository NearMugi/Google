cd /d %~dp0\GetImage_M5stack
gcloud functions deploy getDriveImage_M5stack --runtime python37 --trigger-http --region asia-northeast1 --env-vars-file .env.yaml