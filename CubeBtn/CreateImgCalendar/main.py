# Calendarを画像にしてDriveへアップロードする
# M5Stack向けの画像サイズ(320*240)

import sys
from datetime import datetime, timezone, timedelta
import time
import os
import io
import json
import cv2
from io import BytesIO
import numpy as np
from PIL import Image, ImageFont, ImageDraw
import pandas as pd

import httplib2
from googleapiclient.discovery import build
from oauth2client import client, GOOGLE_TOKEN_URI
from apiclient.http import MediaIoBaseDownload
from googleapiclient.http import MediaFileUpload


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


def getCalendarService():
    print("[%s]" % (sys._getframe().f_code.co_name))

    CLIENT_ID = os.getenv("calendar_client_id")
    CLIENT_SECRET = os.getenv("calendar_client_secret")
    REFRESH_TOKEN = os.getenv("calendar_refresh_token")

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
    service = build("calendar", "v3", credentials=creds, cache_discovery=False)
    return service


def getCalDict():
    idList = [
        os.getenv("calendarID_Te"),
        os.getenv("calendarID_Fu"),
        os.getenv("calendarID_Sh"),
        os.getenv("calendarID_Sa"),
        os.getenv("calendarID_Fa"),
    ]
    idList = map(lambda x: x + "@group.calendar.google.com", idList)
    calDict = dict(zip(["Te", "Fu", "Sh", "Sa", "Fa"], idList))
    return calDict


def getCalenderDf(service, id, nm, fDay, tDay):
    """get Calender list. return DataFrame
    """
    retDf = pd.DataFrame([], columns=["nm", "start", "end", "summary", "description"])

    fDay += "T00:00:00.000000Z"
    tDay += "T00:00:00.000000Z"
    events_result = (
        service.events()
        .list(
            calendarId=id,
            timeMin=fDay,
            timeMax=tDay,
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
    )
    events = events_result.get("items", [])

    if not events:
        return retDf

    for event in events:
        # print(event)
        start = event["start"].get("dateTime", event["start"].get("date"))
        end = event["end"].get("dateTime", event["end"].get("date"))

        # 終日の場合(時間がない)はendが1日多いので補正する
        if not "T" in end:
            date_dt = datetime.strptime(end, "%Y-%m-%d")
            date_dt -= timedelta(days=1)
            end = date_dt.strftime("%Y-%m-%d")

        if "description" in event.keys():
            description = event["description"]
        else:
            description = ""
        tmpDf = pd.DataFrame(
            [[nm, start, end, event["summary"], description]], columns=retDf.columns
        )
        # print(tmpDf)
        retDf = retDf.append(tmpDf)
    print("[%s] end dataSize : %s" % (sys._getframe().f_code.co_name, str(len(retDf))))

    return retDf


def getSummaryCalendarDf(service, t, span, calDict):
    print("[%s]" % (sys._getframe().f_code.co_name))

    JST = timezone(timedelta(hours=+9), "JST")
    fDay = datetime.fromtimestamp(t, JST).strftime("%Y-%m-%d")
    tDay = datetime.fromtimestamp(t + 60 * 60 * 24 * span, JST).strftime("%Y-%m-%d")

    df = pd.DataFrame([])
    for k, v in calDict.items():
        df = pd.concat([df, getCalenderDf(service, v, k, fDay, tDay)])

    # 曜日を取得する
    tmpDf = df["start"].str.split("+", expand=True)
    tmpDf = tmpDf[0].str.split("T", expand=True)
    weekdayDf = tmpDf[0].map(lambda x: datetime.strptime(x, "%Y-%m-%d").weekday())
    df = pd.concat([df, weekdayDf[0]], axis=1)

    # 日付編集する
    # mm/dd , HH:MM
    tmpDf = df["start"].str.split("+", expand=True)

    tmpDf = tmpDf[0].map(lambda x: x[5:])
    tmpDf = tmpDf[0].replace("(.*)-(.*)", r"\1/\2", regex=True)
    tmpDf = tmpDf[0].map(lambda x: x + "T00:00:00" if x.find("T") < 0 else x)
    tmpDf = tmpDf[0].str.split("T", expand=True)

    tmpDf[1] = tmpDf[1].map(lambda x: x[:5])
    df = pd.concat([df, tmpDf[0], tmpDf[1]], axis=1)
    df = df.drop("start", axis=1)

    if len(df) == 0:
        print("... No Data")
        return False, df

    tmpDf = df["end"].str.split("+", expand=True)
    tmpDf = tmpDf[0].map(lambda x: x[5:])
    tmpDf = tmpDf[0].replace("(.*)-(.*)", r"\1/\2", regex=True)
    tmpDf = tmpDf[0].map(lambda x: x + "T00:00:00" if x.find("T") < 0 else x)
    tmpDf = tmpDf[0].str.split("T", expand=True)

    tmpDf[1] = tmpDf[1].map(lambda x: x[:5])
    df = pd.concat([df, tmpDf[0], tmpDf[1]], axis=1)
    df = df.drop("end", axis=1)

    df.columns = ["nm", "title", "detail", "weekday", "sDay", "sTime", "eDay", "eTime"]
    df = df[["sDay", "sTime", "weekday", "eDay", "eTime", "nm", "title"]]
    df = df.sort_values(["sDay", "sTime"])
    df = df.reset_index(drop=True)

    print("[%s] end" % (sys._getframe().f_code.co_name))
    return True, df


def createImg(calDf, fontPath, savePath):
    """ カレンダーの画像を作成、指定パスに保存する
    """
    print("[%s]" % (sys._getframe().f_code.co_name))

    im = Image.new("RGB", (320, 240), (255, 255, 255))
    draw = ImageDraw.Draw(im)

    font_size = 13
    font = ImageFont.truetype(fontPath, font_size)
    weekdayList = ["(月)", "(火)", "(水)", "(木)", "(金)", "(土)", "(日)"]
    i = 0
    for index, row in calDf.iterrows():
        s = row["sDay"]
        s += weekdayList[row["weekday"]]
        s += " " + row["title"]

        if not (row["sTime"] == "00:00" and row["eTime"] == "00:00"):
            s += " (" + row["sTime"] + "-" + row["eTime"] + ")"
        else:
            if not row["sDay"] == row["eDay"]:
                s += " (-" + row["eDay"] + ")"

        col = "black"
        if row["nm"] == "Te":
            col = "orange"
        if row["nm"] == "Fu":
            col = "green"
        if row["nm"] == "Sh":
            col = "blue"
        if row["nm"] == "Sa":
            col = "yellow"
        if row["nm"] == "Fa":
            col = "brown"

        draw.line((0, 24 * (i + 1), 320, 24 * (i + 1)), fill="black", width=1)
        draw.rectangle((3, 24 * i + 3, 18, 24 * (i + 1) - 3), fill=col)
        draw.text((20, 24 * i + 3), s, fill="black", font=font)
        i += 1
        if i >= 10:
            break

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


def mosaic(src, ratio=0.1):
    """モザイクをかける
    """
    small = cv2.resize(src, None, fx=ratio, fy=ratio, interpolation=cv2.INTER_NEAREST)
    return cv2.resize(small, src.shape[:2][::-1], interpolation=cv2.INTER_NEAREST)


def mosaic_area(src, x, y, width, height, ratio=0.1):
    """一部モザイク
    """
    dst = src.copy()
    dst[y:y + height, x:x + width] = mosaic(
        dst[y:y + height, x:x + width], ratio
    )
    return dst


def createDemoCalendar(fromData, toData):
    """ デモ用の画像を作成する
    """
    print("[%s] %s -> %s" % (sys._getframe().f_code.co_name, fromData, toData))
    im = cv2.imread(fromData)

    for i in range(10):
        im = mosaic_area(im, 89, 24 * i + 3, 250, 21, ratio=0.45)

    try:
        cv2.imwrite(toData, im)
    except FileNotFoundError:
        print("...error savePath : %s" % toData)
        return False

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


def CreateImgCalendar(event, context):
    """ get calendarImage and upload to drive for M5stack
    """

    # 準備
    driveService = getDriveService()
    calendarService = getCalendarService()
    calDict = getCalDict()
    fontPath = getFontFromDrive(driveService, "meiryo.ttc")
    if not fontPath:
        return False

    # カレンダーを取得にする
    ret, calDf = getSummaryCalendarDf(calendarService, time.time(), 30, calDict)
    if not ret:
        return False

    # 画像を作って保存する
    ret = createImg(calDf, fontPath, "/tmp/imgCalendar.jpeg")
    if not ret:
        return False

    # デモ用の画像を作って保存する
    ret = createDemoCalendar("/tmp/imgCalendar.jpeg", "/tmp/imgCalendar_Demo.jpeg")
    if not ret:
        return False

    # Driveにアップロードする
    ret = uploadData(
        driveService, "image/jpeg", "/tmp/imgCalendar.jpeg", "imgCalendar.jpeg"
    )
    if not ret:
        return False

    ret = uploadData(
        driveService,
        "image/jpeg",
        "/tmp/imgCalendar_Demo.jpeg",
        "imgCalendar_Demo.jpeg",
    )
    if not ret:
        return False
    else:
        return True
