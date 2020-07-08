# Driveから画像を取得、M5Stack向けにTrimしたバイナリーデータを返す
# input例
# {"drive" : {"img" : "imgCalendar.jpeg", "trim" : "1"} }

# Driveのサービスを取得する部分のビルドでエラーが出ていたので回避
# https://qiita.com/kai_kou/items/4b754c61ac225daa0f7d

import sys
import os
import io
from io import BytesIO
import numpy as np
from PIL import Image

import httplib2
from googleapiclient.discovery import build
from oauth2client import client, GOOGLE_TOKEN_URI
from apiclient.http import MediaIoBaseDownload


def getDriveService():
    print("[%s]" % (sys._getframe().f_code.co_name))

    CLIENT_ID = os.getenv("drive_client_id")
    CLIENT_SECRET = os.getenv("drive_client_secret")
    REFRESH_TOKEN = os.getenv("drive_refresh_token")

    creds = client.OAuth2Credentials(
        access_token=None,
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        refresh_token=REFRESH_TOKEN,
        token_expiry=None,
        token_uri=GOOGLE_TOKEN_URI,
        user_agent=None,
        revoke_uri=None,
    )
    http = creds.authorize(httplib2.Http())

    creds.refresh(http)
    service = build("drive", "v3", credentials=creds, cache_discovery=False)
    return service


# ID検索
def searchID(drive_service, mimetype, nm):
    print("[%s] %s" % (sys._getframe().f_code.co_name, nm))
    query = "mimeType='" + mimetype + "'"
    page_token = None
    while True:
        req = drive_service.files().list(
            q=query,
            spaces="drive",
            fields="nextPageToken, files(id, name)",
            pageToken=page_token,
        )
        response = req.execute()
        print(response)

        for file in response.get("files", []):
            if file.get("name") == nm:
                print("[%s] end Found" % (sys._getframe().f_code.co_name))
                return True, file.get("id")

        page_token = response.get("nextPageToken", None)
        if page_token is None:
            break

    print("[%s] end NotFound" % (sys._getframe().f_code.co_name))
    return False, None


def downloadData(mimetype, data):
    print("[%s] %s" % (sys._getframe().f_code.co_name, data))

    drive_service = getDriveService()

    # IDを検索
    ret, id = searchID(drive_service, mimetype, data)
    if not ret:
        return False, None

    request = drive_service.files().get_media(fileId=id)
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()

    print("[%s] end" % (sys._getframe().f_code.co_name))
    return True, fh.getvalue()


def devideImage_M5stack(imgBinary, _trim):
    """M5Stack用に画像を分割する。返値はイメージデータ
    """
    imgNumpy = 0x00

    # 入力データの確認
    if _trim.isnumeric():
        trimPos = int(_trim)
        if trimPos <= 0 or trimPos > 8:
            return False
    else:
        return False

    # 画像の分割
    # 1 2 3 4
    # 5 6 7 8
    Trim = [
        (0, 0, 80, 120),
        (80, 0, 160, 120),
        (160, 0, 240, 120),
        (240, 0, 320, 120),
        (0, 120, 80, 240),
        (80, 120, 160, 240),
        (160, 120, 240, 240),
        (240, 120, 320, 240),
    ]

    # PILイメージ <- バイナリーデータ
    img_pil = Image.open(BytesIO(imgBinary))

    # トリミング
    print(Trim[trimPos - 1])
    im_crop = img_pil.crop(Trim[trimPos - 1])

    # numpy配列(RGBA) <- PILイメージ
    imgNumpy = np.asarray(im_crop)

    return True, imgNumpy


def getBinary(img):
    """画像をバイナリデータへ変換
    """
    ret = ""
    pilImg = Image.fromarray(np.uint8(img))
    output = io.BytesIO()
    pilImg.save(output, format="JPEG")
    ret = output.getvalue()
    print(
        "[画像をバイナリデータへ変換]"
        + str(type(img))
        + ","
        + str(img.shape[:3])
        + " -> "
        + str(type(ret))
        + ","
        + str(len(ret))
    )

    return ret


def getDriveImg_Binary(imgName, trim):
    """googleDriveに保存してある画像を取得する。返値はバイナリーデータ。
    """
    print("[%s] %s" % (sys._getframe().f_code.co_name, imgName))

    img = 0x00

    # Driveから画像(バイナリーデータ)を取得
    ret, imgBinary = downloadData("image/jpeg", imgName)
    if not ret:
        print("...error")
        return ""

    print(ret, len(imgBinary))

    # 画像を分割する
    # ※M5Stack専用
    if trim is not None:
        isGet, img = devideImage_M5stack(imgBinary, trim)
        if not isGet:
            return ""

        # バイナリデータに変換する
        imgBinary = getBinary(img)

    return imgBinary


def getDriveImage_M5stack(request):
    imgName = ""
    trim = "0"

    # リクエストデータ(JSON)を変換
    request_json = request.get_json()

    # Driveへのアクセス情報を取得
    if request_json and "drive" in request_json:
        imgName = request_json["drive"]["img"]
        trim = request_json["drive"]["trim"]
    else:
        return ""

    ret = getDriveImg_Binary(imgName, trim)

    return ret
