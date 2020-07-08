import json


def helloWorld(request):
    """リクエストを編集して返す
    """

    ret = 'nothing...'

    # request info (flask.Request)
    print(request)
    print(request.method)
    cType = request.headers.get("Content-Type")
    cLength = request.headers.get("Content-Length")
    cData = request.get_json()
    print("[Content] %s, %s, %s" % (cType, cLength, cData))

    # リクエストデータ(JSON)を変換
    request_json = json.loads(request.get_json())
    if request_json and 'data' in request_json:
        ret = request_json['data']
        ret += ret
    print(ret)

    return ret
