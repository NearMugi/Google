import sys

def GetRuntimeConfig_python(request):
    """RuntimeConfigにアクセスする
    """
    import urllib.request

    #Oauthの認証が通らずリクエストエラー(401)。

    url = "https://runtimeconfig.googleapis.com/v1beta1/projects/[プロジェクト名]/configs/[リスト名]/variables/[値]"
    response = urllib.request.urlopen(url)
    print(response)

    return 'True'
