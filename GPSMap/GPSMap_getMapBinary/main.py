# +++++++++++++++
# M5Stack向け 
# +++++++++++++++

# 地図画像(バイナリデータ)を取得する
# 画像サイズが大きすぎるので分割して取得する
# リクエストの形式
#{
#  "key": "hoge",
#  "ts" : "yy/mm/dd hh:mm:ss",
#  "axis":"35.68035,139.7673229",
#  "color":"true",
#  "trim" :"1","2","3","4",
#          "5","6","7","8"
#}



import googlemaps

import cv2
import numpy as np
import io
from PIL import Image, ImageDraw
import array

from datetime import datetime, timezone, timedelta
import time

imgColor = 0x00
imgGray = 0x00

def createMapImage(_key, _ts, _axis, _trim):
    import urllib.request
    global imgColor
    global imgGray
    
    #入力データの確認
    if len(_key) <= 0:
        return False
    
    if len(_axis) <= 0:
        return False

    if _trim.isnumeric():
        trimPos = int(_trim)
        if trimPos <= 0 or trimPos > 8:
            return False
    else:
        return False

    #住所
    address = ''
    try:
        gmaps = googlemaps.Client(key=_key)
    except:
        print("[ERROR] googlemaps.Client")
        return False
    
    try:
        results = gmaps.reverse_geocode(_axis)
    except:
        print("[ERROR] gmaps.reverse_geocode")
        return False

    for result in results:
        if result['types'] == ['political', 'sublocality', 'sublocality_level_3']:
            address = result['formatted_address'].split(', ')
            address.reverse()
            break

    print(address)    
    
    #地図
    baseURL = "https://maps.googleapis.com/maps/api/staticmap?center=@axis"
    baseURL += "&maptype=@maptype&size=@size&sensor=false&zoom=@zoom&markers=@axis"
    baseURL += "&key=@key"
    
    # M5Stack向けの設定値
    maptype = 'roadmap'
    zoom = '17'
    size = '320x240'
    #画像の分割
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
    
    url = baseURL.replace('@maptype', maptype).replace('@axis', _axis).replace('@zoom', zoom).replace('@size', size).replace('@key', _key)
    #print(url)

    #baseMapURL = "https://www.google.co.jp/maps/@@axis,@zoomz?hl=ja"
    #mapURL = baseMapURL.replace('@axis', _axis).replace('@zoom', zoom)
    #print(mapURL)
    
    try:
        response = urllib.request.urlopen(url)
    except:
        print("[ERROR] urllib.request.urlopen")
        return False
    
    img = response.read()
    img_binarystream = io.BytesIO(img)

    #PILイメージ <- バイナリーストリーム
    img_pil = Image.open(img_binarystream).convert('RGB')

    # 住所を書き込む
    b = (164, 90, 255)
    p = (255, 255, 120)
    draw = ImageDraw.Draw(img_pil)
    draw.rectangle((10, 10, 150, 60), fill=b, outline=b)
    
    draw.text((15,15), _ts, fill=p)
        
    if address != '':
        draw.text((15,25),address[1], fill=p)
        draw.text((15,35),address[2], fill=p)
        draw.text((15,45),address[3], fill=p)
    else:        
        print("[WARNING] there is no address")
        draw.text((15,25),"there is no address", fill=p)

    #トリミング
    print(Trim[trimPos - 1])
    im_crop = img_pil.crop(Trim[trimPos - 1])
    
    #numpy配列(RGBA) <- PILイメージ
    imgColor = np.asarray(im_crop)
    #グレースケール
    imgGray = cv2.cvtColor(imgColor, cv2.COLOR_RGB2GRAY)
    
    return True

    
def getBinary(img):    
    """画像をバイナリデータへ変換
    """
    ret = ""
    pilImg = Image.fromarray(np.uint8(img))
    output = io.BytesIO()
    pilImg.save(output, format='JPEG')
    ret = output.getvalue()
    print('[画像をバイナリデータへ変換]'+ str(type(img)) + ',' + str(img.shape[:3])+ ' -> ' + str(type(ret)) + ',' + str(len(ret)))
    
    return ret


def GPSMap_getMapBinary(request):
    """指定した緯度・経度の画像(バイナリデータ)を返す
    """

    key = ''
    ts = ''
    axis = "0.0,0.0"
    isColor = "true"

    #リクエストデータ(JSON)を変換
    request_json = request.get_json()
    if request_json and 'key' in request_json:
        key = request_json['key']

    if request_json and 'ts' in request_json:
        ts = request_json['ts']        

    if request_json and 'axis' in request_json:
        axis = request_json['axis']        

    if request_json and 'color' in request_json:
        isColor = request_json['color']

    if request_json and 'trim' in request_json:
        trim = request_json['trim']

    #地図画像を作成
    isGet = createMapImage(key,ts,axis,trim)
    if not isGet:
        return ""

    #バイナリデータ取得
    if isColor.lower() == "true":
        ret = getBinary(imgColor)
    else:
        ret = getBinary(imgGray)

    return ret
