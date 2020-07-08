from linebot import LineBotApi
from linebot.models import ImageSendMessage
import json


def linebotSendImage(request):
    """LINEのグループIDに画像を送信する
    """

    reqOriginalURL = ""
    reqPreviewURL = ""
    channelAccessToken = ""
    sendGroupId = ""

    # リクエストデータ(JSON)を変換
    request_json = request.get_json()
    if request_json and 'reqOriginalURL' in request_json:
        reqOriginalURL = request_json['reqOriginalURL']

    if request_json and 'reqPreviewURL' in request_json:
        reqPreviewURL = request_json['reqPreviewURL']

    if request_json and 'channelAccessToken' in request_json:
        channelAccessToken = request_json['channelAccessToken']

    if request_json and 'sendGroupId' in request_json:
        sendGroupId = request_json['sendGroupId']

    line_bot_api = LineBotApi(channelAccessToken)

    image_message = ImageSendMessage(
        original_content_url=reqOriginalURL,
        preview_image_url=reqPreviewURL,
    )
    line_bot_api.push_message(sendGroupId, image_message)

    return json.dumps({'end': True})
