import sys
import cv2
import numpy as np
from PIL import Image
import array

import nnabla as nn
import nnabla.functions as F
import nnabla.parametric_functions as PF

from google.cloud import storage


import os
import io
from apiclient.http import MediaIoBaseDownload

from googleapiclient.discovery import build
drive_service = build('drive', 'v3')

def network(x, test=False):
    # Input:x -> 3,60,80

    # Affine -> 256
    h = PF.affine(x, (256,), name='Affine')
    # ReLU
    h = F.relu(h, True)
    # Dropout
    if not test:
        h = F.dropout(h)

    # Affine_2 -> 4
    h = PF.affine(h, (4,), name='Affine_2')
    # Softmax
    h = F.softmax(h)
    return h

def get_file(projectNm, bucketNm, fileNm):
    """GCSからファイルを取得
    """
    storage_client = storage.Client(project=projectNm)
    bucket = storage_client.get_bucket(bucketNm)
    return bucket.get_blob(fileNm)

def download(_fileID,_path,_fn):
    """Driveにあるファイルをダウンロード
    """
    request = drive_service.files().get_media(fileId=_fileID)
    fh = io.FileIO(_path + '/' + _fn, 'wb') #ファイル

    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()
        print("Download %d%%." % int(status.progress() * 100))
    print(fh)
    
    return fh

def CW_nnc(request):
    import struct
    import json

    _basePath = '/tmp'  #ファイルの保存フォルダ
    _imageFn = 'image.jpeg'  #取得した画像ファイル名
    _ratio = 20         #縮小倍率(1/n)

    _studyFile = 'results.nnp'

    #リクエストデータ(JSON)を変換
    request_json = request.get_json()
#    print(request_json['studyData']['data'])

    #学習データはGoogleDriveからダウンロードする
    if request_json and 'studyData' in request_json:
        download(request_json['studyData']['fileID'], _basePath, _studyFile)
    else:
        return 'No studyData'

    #画像データ(バイナリデータ)を取得して学習
    if request_json and 'inputData' in request_json:

        # load parameters
        nn.load_parameters(_basePath + '/' + _studyFile)

        # Prepare input variable
        x=nn.Variable((1,3,60,80))

        _list = request_json['inputData']['data']
        #バイナリデータに変換
        _binary = array.array('B', _list).tobytes()       
        #バイナリーストリーム <- バリナリデータ
        img_binarystream = io.BytesIO(_binary)
        #PILイメージ <- バイナリーストリーム
        img_pil = Image.open(img_binarystream)
        #numpy配列(RGBA) <- PILイメージ
        img_numpy = np.asarray(img_pil)
        #numpy配列(BGR) <- numpy配列(RGBA)
        resizeImg = cv2.cvtColor(img_numpy, cv2.COLOR_RGBA2BGR)

        # Let input data to x.d
        #輝度を0.0～1.0に変換
        resizeImg = resizeImg.astype(np.float)/255.0   

        #(h, w, c)から(c, h, w)への変換
        #print('(h,w,c) : ' + str(resizeImg.shape[:3]))
        im = np.transpose(resizeImg, (2, 0, 1))
        #print('(c,h,w) : ' + str(im.shape[:3]))
        x = nn.Variable((1, ) + im.shape)
        x.d = im.reshape(x.shape)

        # Build network for inference
        y = network(x, test=True)

        # Execute inference
        y.forward()
        print(y.d)

        ret = json.dumps(y.d.tolist(), ensure_ascii=False, indent=4, sort_keys=True, separators=(',', ': '))
        return ret        

    else:
       return 'No inputData'

