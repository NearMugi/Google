
#Driveからダウンロード
# サンプルを少し変えている
# https://developers.google.com/drive/api/v3/manage-downloads
# https://stackoverflow.com/questions/36173356/google-drive-api-download-files-python-no-files-downloaded


import os
import io
import json
from apiclient.http import MediaIoBaseDownload

from googleapiclient.discovery import build
drive_service = build('drive', 'v3')

def download_binary(_fileID):
    """バイナリーデータを取得
    """
    request = drive_service.files().get_media(fileId=_fileID)
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()
        print("Download %d%%." % int(status.progress() * 100))
    print(len(fh.getvalue()))
    
    return fh.getvalue()
    


def download(_fileID,_path,_fn):
    """ファイルにダウンロード
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

def Drive_download_py(request):
    _fileID = ''
    _path = ''  #ファイルの保存フォルダ
    _fn = ''  #保存するファイル名

    #リクエストデータ(JSON)を変換
    request_json = request.get_json()
#    print(request_json['studyData']['data'])

    #Driveへのアクセス情報を取得
    if request_json and 'drive' in request_json:
        _fileID = request_json['drive']['fileID']
        _path = request_json['drive']['path']
        _fn = request_json['drive']['fn']
    else:
        return 'No DriveInfo'
        
    download(_fileID,_path,_fn)
    f = download_binary(_fileID)
    #print(f)

    return json.dumps({'end' : True, 'fileSize' : len(f)})
