import firebase_admin
from firebase_admin import firestore

# 初期化済みのアプリが存在しないか確認する。※複数アプリの初期化はエラーです。的な例外に遭遇したので入れたif文
if len(firebase_admin._apps) == 0:
    # アプリを初期化する
    default_app = firebase_admin.initialize_app()
db = firestore.client()

def FirebaseSample(request):
    # firestoreに書き込み
    db.collection('1400').document('docid').set({"foo": "bar"})
    # ブラウザに見せるために返す
    return f'Hello World!'