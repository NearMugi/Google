import sys

from google.cloud import storage

def get_file(projectNm, bucketNm, fileNm):
    """GCSからファイルを取得
    """
    storage_client = storage.Client(project=projectNm)
    bucket = storage_client.get_bucket(bucketNm)
    return bucket.get_blob(fileNm)

def Storage_Download(request):
    import struct
    import json

    _basePath = '/tmp'  #ファイルの保存フォルダ
    _imageFn = 'image.jpeg'  #保存する画像ファイル名

    #リクエストデータ(JSON)を変換
    request_json = request.get_json()
#    print(request_json['studyData']['data'])

    if request_json and 'saveData' in request_json:
        _basePath = request_json['saveData']['Path']
        _imageFn = request_json['saveData']['Fn']

    #データ(バイナリデータ)
    if request_json and 'inputData_Binary' in request_json:
        binary = request_json['inputData_Binary']['data']
        with open(_basePath + '/' + _imageFn, 'wb') as f:
            for b in binary:
                f.write(struct.pack("B", b))                
    else:
        #バイナリーデータではなく、ファイル指定の場合
        if request_json and 'inputData' in request_json:
            file = get_file(request_json['inputData']['project'],
                            request_json['inputData']['bucket'],
                            request_json['inputData']['Path'] + '/' + request_json['inputData']['Fn'])
            file.download_to_filename(_basePath + '/' + _imageFn)                
        else:
            return 'No inputData'

    return True
