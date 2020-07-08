# LINEBOT関係

## Fromline

### line(lineAPI) -> CloudFunctions -> Beebotte -> Node-Red -> GoogleHomeMini

## ToLine

### GoogleHomeMini -> ifttt(Webhook) -> CloudFunctions -> line(lineAPI)

## Line_GoogleHome

### Merge 'Fromline' and 'ToLine'

## Line_SendImage

LINEのグループトークに画像メッセージを送信する

### リクエスト

reqOriginalURL: メイン画像URL
reqPreviewURL: プレビュー用画像URL
channelAccessToken: LINEのチャンネルアクセストークン
channelSecret: LINEのチャンネルシークレット
sendGroupId: LINEのグループID

### グループIDの取得方法

1. グループを作る
2. GCFのreqCheckをLINEのMessageAPIのWebhookにする
3. 適当なコメントをグループに書き込む
4. reqCheckのログを見るとgroupIDが分かる
