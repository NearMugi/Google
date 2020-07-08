# 天気予報を画像にしてDriveへアップロードする
# M5Stack向けの画像サイズ(320*240)

import sys
from datetime import datetime, timezone, timedelta
import time
import os
import io
import json
import cv2
from io import BytesIO

import httplib2
from googleapiclient.discovery import build
from oauth2client import client, GOOGLE_TOKEN_URI
from apiclient.http import MediaIoBaseDownload
from googleapiclient.http import MediaFileUpload


import re
from urllib.request import Request, urlopen
import urllib.request
from urllib.error import HTTPError
from urllib.error import URLError
from bs4 import BeautifulSoup
from PIL import Image, ImageFont, ImageDraw


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


def getHTML(URL):
    "htmlの取得"
    try:
        req = Request(URL, headers={"User-Agent": "Mozilla/5.0"})
        html = urlopen(req)
    except HTTPError as e:
        print(e)
    except URLError as e:  # サーバーに全く到達できない(URLの記述が間違えているなど)
        print("The server could not be found!")
    else:
        return html


def getBS4(html):
    "BsObjの取得"
    return BeautifulSoup(html.read(), "html.parser")


def getWeekWeather():
    url = "http://www.jma.go.jp/jp/yoho/319.html"
    html = getHTML(url)
    bsObj = getBS4(html)
    # print(bsObj.prettify())
    table = bsObj.find("table", attrs={"class": "forecast"})
    tableList = list()

    date = table.findAll("th", attrs={"class": "weather"})
    weather = table.findAll("th", attrs={"class": "weather"})
    info = table.findAll("td", attrs={"class": "info"})
    rain = table.findAll("td", attrs={"class": "rain"})
    temp = table.findAll("td", attrs={"class": "temp"})
    for d, w, i, r, t in zip(date, weather, info, rain, temp):
        # 日付
        tmpD = d.get_text().replace("\n", "")

        if w.find("img") is None:
            tmpW = ""
            tmpI = ""
            tmpR = []
            tmpT = ("", "", "")
        else:
            # 天気
            tmpW = w.find("img")["title"]

            # info 波の高さはいらない
            tmpI = re.sub("波.*", "", i.get_text())
            tmpI = tmpI.replace("　", " ")

            # 降水確率
            tmpRt = r.findAll("td", attrs={"align": "left"})
            tmpRt = [t.get_text() for t in tmpRt]
            tmpRp = r.findAll("td", attrs={"align": "right"})
            tmpRp = [p.get_text() for p in tmpRp]
            tmpR = list(zip(tmpRt, tmpRp))

            # 気温
            # 気温が書いてある場合とない場合がある
            tmpT = ("", "", "")
            city = t.find("td", attrs={"class": "city"})
            min_ = t.find("td", attrs={"class": "min"})
            max_ = t.find("td", attrs={"class": "max"})
            if city is not None:
                tmpT = (
                    city.get_text(),
                    min_.get_text(),
                    max_.get_text().replace("\n", "").replace("\t", ""),
                )

        tableList.append((tmpD, tmpW, tmpI, tmpR, tmpT))

    # 東京分だけを返す
    return tableList[:3]


# ## 画像を作成する
def createImg(fontPath, savePath, weatherList):
    print("[%s]" % (sys._getframe().f_code.co_name))

    im = Image.new("RGB", (320, 240), (255, 255, 255))
    draw = ImageDraw.Draw(im)

    i = 0
    for wl in weatherList:
        # print(wl)

        # 日にち
        day = wl[0]
        font_size = 16
        font = ImageFont.truetype(fontPath, font_size)
        draw.text((105 * i + 10, 3), day, fill="black", font=font)

        # 天気
        weather = wl[1]
        font_size = 16
        font = ImageFont.truetype(fontPath, font_size)
        draw.text((105 * i + 10, 115 + 3), weather, fill="black", font=font)

        # 気温
        temp = ""
        if len(wl[4][2]) > 0:
            if len(wl[4][1]) > 0:
                temp = wl[4][1] + "～" + wl[4][2]
            else:
                temp = "　　～" + wl[4][2]
        else:
            temp = "nothing"
        font_size = 16
        font = ImageFont.truetype(fontPath, font_size)
        draw.text((105 * i + 10, 135 + 3), temp, fill="black", font=font)

        # 降水確率
        rain = "00-06 : --%" + "\n"
        rain += "06-12 : --%" + "\n"
        rain += "12-18 : --%" + "\n"
        rain += "18-24 : --%"
        if len(wl[3]) > 0:
            rain = wl[3][0][0] + " : " + wl[3][0][1] + "\n"
            rain += wl[3][1][0] + " : " + wl[3][1][1] + "\n"
            rain += wl[3][2][0] + " : " + wl[3][2][1] + "\n"
            rain += wl[3][3][0] + " : " + wl[3][3][1]

        font_size = 13
        font = ImageFont.truetype(fontPath, font_size)
        draw.text((105 * i + 10, 160 + 3), rain, fill="black", font=font)

        # 天気(画像)
        # 左上(x, y) サイズ 70 * 80
        # p1 : 左上
        # p2 : 中央 + オフセット
        x = 105 * i + 10
        y = 30
        lenX = 70
        lenY = 80
        p1 = (x, y)
        p2 = (x + int(lenX / 4), y + int(lenY / 4))

        color = ["noImage.png", ""]
        j = 0
        for s in weather:
            if s == "晴":
                color[j] = "fine.png"
                j += 1
            if s == "曇":
                color[j] = "cloud.png"
                j += 1
            if s == "雨":
                color[j] = "rain.png"
                j += 1
            if s == "雪":
                color[j] = "snow.png"
                j += 1

            if j > 1:
                break

        if j <= 1:
            img = Image.open("/tmp/" + color[0])
            im.paste(img, p1, img)
        elif j == 2:
            img = Image.open("/tmp/" + color[0])
            img = img.resize((int(lenX / 2 * 1.5), int(lenY / 2 * 1.5)))
            im.paste(img, p1, img)
            img = Image.open("/tmp/" + color[1])
            img = img.resize((int(lenX / 2 * 1.5), int(lenY / 2 * 1.5)))
            im.paste(img, p2, img)

        i += 1

    try:
        im.save(savePath, quality=95)
    except FileNotFoundError:
        print("...error savePath : %s" % savePath)
        return False

    print("[%s] end" % (sys._getframe().f_code.co_name))
    return True


def searchID(service, mimetype, nm):
    """Driveから一致するIDを探す
    """
    print("[%s] %s" % (sys._getframe().f_code.co_name, nm))
    query = ""
    if mimetype:
        query = "mimeType='" + mimetype + "'"

    page_token = None
    while True:
        response = (
            service.files()
            .list(
                q=query,
                spaces="drive",
                fields="nextPageToken, files(id, name)",
                pageToken=page_token,
            )
            .execute()
        )

        for file in response.get("files", []):
            if file.get("name") == nm:
                print("[%s] end Found" % (sys._getframe().f_code.co_name))
                return True, file.get("id")

        page_token = response.get("nextPageToken", None)
        if page_token is None:
            break

    print("[%s] end NotFound" % (sys._getframe().f_code.co_name))
    return False, None


def getFontFromDrive(service, fontName):
    """フォントをDriveから取得、tmpフォルダに保存する
    """
    ret, id = searchID(service, "application/octet-stream", fontName)
    if not ret:
        return None

    request = service.files().get_media(fileId=id)
    fh = io.FileIO("/tmp/" + fontName, "wb")  # ファイル

    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()

    return "/tmp/" + fontName


def getImageFromDrive(service, imageName):
    """画像をDriveから取得、tmpフォルダに保存する
    """
    ret, id = searchID(service, "image/png", imageName)
    if not ret:
        return False

    request = service.files().get_media(fileId=id)
    fh = io.FileIO("/tmp/" + imageName, "wb")  # ファイル

    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()

    return True


def getImageFromDriveByID(service, imageName, imageID):
    """画像をDriveからIDを指定して取得、tmpフォルダに保存する
    """
    request = service.files().get_media(fileId=imageID)
    fh = io.FileIO("/tmp/" + imageName, "wb")  # ファイル

    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()

    return True


def uploadData(service, mimetype, fromData, toData, parentsID="root"):
    """ Driveにアップロードする
    """
    print("[%s] %s -> %s" % (sys._getframe().f_code.co_name, fromData, toData))

    try:
        media = MediaFileUpload(fromData, mimetype=mimetype, resumable=True)
    except FileNotFoundError:
        print("... Not Found updateData : %s" % fromData)
        return False

    # IDを検索、該当するデータがある場合は上書きする。
    ret, id = searchID(service, mimetype, toData)
    if ret:
        file_metadata = {"name": toData}

        file = (
            service.files()
            .update(fileId=id, body=file_metadata, media_body=media, fields="id")
            .execute()
        )
    else:
        file_metadata = {"name": toData, "parents": [parentsID]}

        file = (
            service.files()
            .create(body=file_metadata, media_body=media, fields="id")
            .execute()
        )

    print("[%s] end" % (sys._getframe().f_code.co_name))
    return True


def CreateImgWeather(event, context):
    """ get weatherImage and upload to drive for M5stack
    """

    # 準備
    driveService = getDriveService()

    # フォント
    if not getImageFromDriveByID(driveService, "meiryo.ttc", os.getenv("fontID")):
        return False

    # 天気画像
    if not getImageFromDriveByID(driveService, "noImage.png", os.getenv("noImageID")):
        return False
    if not getImageFromDriveByID(driveService, "fine.png",  os.getenv("fineID")):
        return False
    if not getImageFromDriveByID(driveService, "cloud.png", os.getenv("cloudID") ):
        return False
    if not getImageFromDriveByID(driveService, "rain.png", os.getenv("rainID")):
        return False
    if not getImageFromDriveByID(driveService, "snow.png", os.getenv("snowID")):
        return False

    # 天気データを取得する
    weatherList = getWeekWeather()

    # 画像を作って保存する
    ret = createImg("/tmp/meiryo.ttc", "/tmp/imgWeather.jpeg", weatherList)
    if not ret:
        return False

    # Driveにアップロードする
    ret = uploadData(
        driveService, "image/jpeg", "/tmp/imgWeather.jpeg", "imgWeather.jpeg"
    )
    if not ret:
        return False

    return True
