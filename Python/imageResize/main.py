# 画像(バイナリデータ)を縮小する
# http://peaceandhilightandpython.hatenablog.com/entry/2016/01/09/214333
# https://qiita.com/rrryutaro/items/ce6634a37a257adc4fb1

import sys
import io
import numpy as np
import cv2
import requests
from PIL import Image
import array

def resize(_binary, _ratio):
    """
    画像(バイナリデータ)を縮小
    変換後の画像(numpy.ndarray)を返す
    _binary : 画像(バイナリデータ)
    _ratio : 縮小倍率(1/n) 10なら1/10
    """
    print('ratio :' + str(_ratio))
    
    #バイナリーストリーム <- バリナリデータ
    img_binarystream = io.BytesIO(_binary)
    print('バイナリーストリーム , ' + str(type(img_binarystream)) +' , '+ str(len(img_binarystream.getvalue())) )

    #PILイメージ <- バイナリーストリーム
    #この段階だとRGBA
    img_pil = Image.open(img_binarystream)
    print('PILイメージ , ' + str(type(img_pil)) +' , '+ str(img_pil.size) +' , '+ str(img_pil.mode)) 

    #numpy配列(RGBA) <- PILイメージ
    img_numpy = np.asarray(img_pil)
    print('numpy配列(RGBA) , ' + str(type(img_numpy)) +' , '+ str(img_numpy.size) +' , '+ str(img_numpy.shape[:3]))

    #numpy配列(BGR) <- numpy配列(RGBA)
    img_numpy_bgr = cv2.cvtColor(img_numpy, cv2.COLOR_RGBA2BGR)
    print('numpy配列(BGR) , ' + str(type(img_numpy_bgr)) +' , '+ str(img_numpy_bgr.size) +' , '+ str(img_numpy_bgr.shape[:3]))

    # 縮小
    orgHeight, orgWidth = img_numpy_bgr.shape[:2]
    size = (int(orgWidth/_ratio), int(orgHeight/_ratio) )
    resizeImg = cv2.resize(img_numpy_bgr, size, interpolation = cv2.INTER_LINEAR)
    print('縮小 , ' + str(size) +' , '+ str(type(resizeImg)) +' , '+ str(resizeImg.size) +' , '+ str(resizeImg.shape[:3]))

    #RGBの並びに変換する
    resizeImg_rgb = cv2.cvtColor(resizeImg, cv2.COLOR_BGR2RGB)
    print('縮小(RGB) , ' + str(type(resizeImg_rgb)) +' , '+ str(resizeImg_rgb.size) +' , '+ str(resizeImg_rgb.shape[:3]))
    
    return resizeImg_rgb

def imageResize(request):
    """バイナリーデータを受け取って縮小、バイナリーデータを返す
    """
    import struct
    import json

    _ratio = 1

    #リクエストデータ(JSON)を変換
    request_json = request.get_json()
    #print(request_json)

    if request_json and 'ratio' in request_json:
        _ratio = request_json['ratio']

    if request_json and 'data' in request_json:
        #バイナリーデータのリストを取得
        _list = request_json['data']['data']
        #print(type(_list))
        #print(_list)

        #バイナリデータに変換
        binary = array.array('B', _list).tobytes()
        #print(type(binary))
        #print(binary)
        
        #縮小
        resizeImg = resize(binary, _ratio)
        #print(resizeImg[0])

        #縮小した画像をバイナリデータへ変換
        pilImg = Image.fromarray(np.uint8(resizeImg))
        output = io.BytesIO()
        pilImg.save(output, format='JPEG')
        ret = output.getvalue()
        print('縮小した画像をバイナリデータへ変換 , ' + str(type(ret)) + ' , ' + str(len(ret)))

        return ret        
    else:
        return 0x00


