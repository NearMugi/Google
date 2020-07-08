cd /d %~dp0\TweetsAddFirebase
gcloud functions deploy TweetsAnalysis --runtime python37 --trigger-resource twitterAnalysis --trigger-event google.pubsub.topic.publish --region asia-northea
st1 --memory 1024MB