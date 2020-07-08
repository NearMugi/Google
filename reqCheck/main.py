import json


def reqCheck(request):
    """
    リクエストを表示するだけ
    """

    request_json = request.get_json()
    print(request_json)
    return json.dumps({"result": True})
