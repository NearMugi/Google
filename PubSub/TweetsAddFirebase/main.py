from datetime import datetime
from pytz import timezone

import firebase_admin
from firebase_admin import firestore

import json
import pandas as pd
from requests_oauthlib import OAuth1Session

# 現在の最大表示列数の出力
pd.get_option("display.max_columns")
# 最大表示列数の指定
pd.set_option("display.max_columns", 50)

global db
global twitter_api

# 検索ワードを管理するFireStoreコレクション名
global ManageCollection
ManageCollection = "Twitter"

# 取得したデータを一時ストックするFireStoreコレクション名
global StockCollection
StockCollection = "TwitterStock"

# タイムラインのツイートをまとめるドキュメント
global TimelineDoc
TimelineDoc = "TimeLine"


def firebaseInit():
    global db
    # 初期化済みのアプリが存在しないか確認する。
    if len(firebase_admin._apps) == 0:
        # アプリを初期化する
        firebase_admin.initialize_app()
    db = firestore.client()


class TwitterApi:
    def __init__(self, att):
        API_K = att["API_KEY"]
        API_S = att["API_SECRET"]
        TOKEN_K = att["TOKEN_KEY"]
        TOKEN_S = att["TOKEN_SECRET"]

        self.twitter_api = OAuth1Session(API_K, API_S, TOKEN_K, TOKEN_S)
        self.url = ""
        self.params = {}
        self.params["count"] = 200
        self.params["result_type"] = "recent"
        self.params["exclude"] = "retweets"
        self.lastID = "0"

    def setParam_Search(self, searchDate_From, searchDate_To):
        """
        検索 : パラメータの設定(共通)
        """
        self.url = "https://api.twitter.com/1.1/search/tweets.json?"
        self.params["tweet_mode"] = "extended"
        self.params["q"] = ""
        self.params["since"] = searchDate_From + "_00:00:00_JST"
        self.params["until"] = searchDate_To + "_23:59:59_JST"

    def setParam_SearchUnit(self, searchWord, lastID):
        """
        検索 : パラメータの設定(各ワード)
        """
        self.params["q"] = searchWord
        self.lastID = "0"
        if len(lastID) > 0:
            self.params["since_id"] = int(lastID)
            self.lastID = lastID

        # max_idが残っている場合は削除する
        try:
            del self.params["max_id"]
        except Exception:
            pass

    def getTweets(self, isSearch):
        req = self.twitter_api.get(self.url, params=self.params)
        print(
            "...URL : {}, Param : {}, Req StatusCode : {},".format(
                self.url, self.params, req.status_code
            )
        )

        # 正常に取得できている場合
        if req.status_code == 200:
            # なぜか残り回数を取得できない場合があるので回避
            try:
                self.limit_remaining = req.headers["X-Rate-Limit-Remaining"]
            except Exception:
                print("...Failed to get X-Rate-Limit-Remaining")
                return False

            # ツイートたちを取得する
            self.tweets = json.loads(req.text)
            if isSearch:
                self.search = self.tweets["search_metadata"]  # 検索条件
                self.tweets = self.tweets["statuses"]
            self.count = len(self.tweets)

            if self.count == 0:
                print("...Nothing Search Data")
                return False

            # Intに変換したとき丸められてしまうので微調整
            if int(self.lastID) - 100 < self.tweets[0]["id"]:
                self.lastID = str(self.tweets[0]["id"])

            # 2回目以降の調整
            self.params["max_id"] = self.tweets[-1]["id"] - 1
            print(
                "...Limit : "
                + self.limit_remaining
                + ", Next Start ID : "
                + str(self.params["max_id"])
            )

            return True

        else:
            print("...request error :{0}".format(req.status_code))
            return False

    def setParam_Timeline(self, lastID):
        """
        タイムラインから取得 : パラメータの設定
        """
        self.url = "https://api.twitter.com/1.1/statuses/home_timeline.json?"
        self.lastID = "0"
        self.params["tweet_mode"] = "extended"
        if len(lastID) > 0:
            self.params["since_id"] = int(lastID)
            self.lastID = lastID


def setDate(f, t):
    """
    日付の設定 : 想定する形式(yyyy-mm-dd)でない場合は当日日付にする
    """
    today = str(datetime.now(timezone("Asia/Tokyo")))
    today = today[:10]
    searchDate_From = today
    searchDate_To = today

    if chkDate(f):
        searchDate_From = f
    if chkDate(t):
        searchDate_To = t

    return searchDate_From, searchDate_To


def chkDate(t):
    """
    想定する日付型かチェックする
    """
    if len(t) != 10:
        return False
    try:
        t = t.replace("-", "/")
        try:
            print(datetime.datetime.strptime(t, "%Y/%m/%d"))
        except Exception:
            return False
    except Exception:
        return False
    return True


def getTweets_Search(_type, _searchWord, _lastID):
    """
    検索条件に従ってツイートを取得する
    """
    global twitter_api
    twitter_api.setParam_SearchUnit(_searchWord, _lastID)
    tweets_df = pd.DataFrame([])

    print("[Start GetTweets] Word : {0}".format(_searchWord))

    while True:
        if not twitter_api.getTweets(True):
            break

        # 取得したデータを保存する
        df = pd.io.json.json_normalize(twitter_api.tweets)
        tweets_df = pd.concat([tweets_df, df], axis=0, sort=True)
        print("...Get! size : {0}".format(str(len(df))))

        # アクセス可能数がゼロ
        if int(twitter_api.limit_remaining) <= 0:
            print("...Limit Access Count")
            break

    print("[End GetTweets] Get tweet data : {0}".format(str(len(tweets_df))))

    return tweets_df


def getTweets_Timeline():
    """
    タイムラインのツイートを取得する
    """
    global twitter_api
    tweets_df = pd.DataFrame([])

    while True:
        if not twitter_api.getTweets(False):
            break
        # 取得したデータを保存する
        df = pd.io.json.json_normalize(twitter_api.tweets)
        tweets_df = pd.concat([tweets_df, df], axis=0, sort=True)
        print("...Get! size : {0}".format(str(len(df))))

        # アクセス可能数がゼロ
        if int(twitter_api.limit_remaining) <= 0:
            print("...Limit Access Count")
            break

    print("[End GetTweets] Total data size: {0}".format(str(len(tweets_df))))

    return tweets_df


def reshapeTweets(tweets_df):
    """
    取得したツイートたちを整形する  必ずここで整形してFireStoreに追加する
    """
    if not len(tweets_df):
        return []

    # 画像・動画のURLを抜き出す
    try:
        tweets_df_url = []
        listMedia = tweets_df["extended_entities.media"]
        for l in listMedia:
            url = []
            if not type(l) == float:
                for i in l:
                    url.append(i["media_url_https"])
                    if i["type"] == "video" or i["type"] == "animated_gif":
                        url.append(i["video_info"]["variants"][0]["url"])
            tweets_df_url.append(url)
        tweets_df["url"] = tweets_df_url
    except Exception:
        print("No extended_entities.media at all")
        noneList = []
        for i in range(len(tweets_df)):
            noneList.append([])
        tweets_df["url"] = noneList

    # IDを文字型に変換
    tweets_df["id"] = tweets_df["id"].astype(str)

    # データの整形
    # 日付をTimeStamp型にして、タイムゾーンを変更
    tweets_df["created_at"] = pd.to_datetime(tweets_df["created_at"])
    tweets_df.index = pd.DatetimeIndex(tweets_df.created_at, name="created_at")
    tweets_df.index = tweets_df.index.tz_convert("Asia/Tokyo")
    tweets_df.created_at = tweets_df.index
    tweets_df = tweets_df.reset_index(drop=True)

    # UNIX時間(エポック秒)を追加する
    tweets_df["epoch"] = tweets_df["created_at"].map(pd.Timestamp.timestamp).astype(int)

    # Timestamp型を文字型に変換
    tweets_df["created_at"] = tweets_df["created_at"].astype(str)

    # 欲しい情報を抜き出す

    # ID
    tweets_ID = tweets_df.loc[:, "id"]
    # print(tweets_ID)

    # ツイートの中身
    tweets_df = tweets_df.loc[
        :, ["created_at", "epoch", "user.name", "user.screen_name", "full_text", "url"]
    ]
    # dictのリストに変換 [{'created_at' : nn, ...},{'created_at' : nn, ...},...]
    tweets_df = tweets_df.to_dict(orient="records")
    # print(tweets_df)

    # 結合
    # {id1:{'created_at' : nn, ...},id2:{'created_at' : nn, ...},...}
    tweets_df = dict(zip(tweets_ID, tweets_df))
    # print(tweets_df)

    return tweets_df


def TweetsCollect_SearchWord(event, context):
    """
    Collect Tweet and add to FireStore
    """
    # attribute {"type" : 種類, "word" : 検索ワード , "from" : 開始日, "to" : 終了日,
    #            "API_KEY" : Twitter関係のKEY}
    # [FireStore]
    # Twitter--Group--SearchWord--TweetID -- {id1:{create_at,text, ...},
    #               --{SearchWord : lastID}   id2:{create_at,text, ...},...}

    firebaseInit()
    att = event["attributes"]

    # 日付の取得
    searchDate_From, searchDate_To = setDate(att["from"], att["to"])

    # 検索条件(list) ( (種類 ,検索ワード, lastID), (種類 ,検索ワード, lastID), ... )
    searchList = []
    db_m = db.collection(ManageCollection)
    if "type" in att and "word" in att:
        id = "0"
        try:
            id = db_m.document(att["type"]).get().to_dict()[att["word"]]
        except Exception:
            pass
        searchList.append((att["type"], att["word"], id))

    else:
        for t in db_m.stream():
            for d in t.to_dict():
                # タイムライン用のコレクションは無視する
                if t.id == TimelineDoc:
                    continue
                searchList.append((t.id, d, db_m.document(t.id).get().to_dict()[d]))

    # 検索条件が揃ったのでTweetを取得、FireStoreに追加
    global twitter_api
    twitter_api = TwitterApi(att)
    twitter_api.setParam_Search(searchDate_From, searchDate_To)
    for l in searchList:
        _type = l[0]
        _searchWord = l[1]
        _lastID = l[2]

        tweetDf = pd.DataFrame([])
        tweetDf = getTweets_Search(_type, _searchWord, _lastID)
        tweetDict = reshapeTweets(tweetDf)
        if len(tweetDict) > 0:
            # 最新のIDを更新
            db.collection(ManageCollection).document(_type).update(
                {_searchWord: twitter_api.lastID}
            )

            # FireStoreに追加(使用量が多く課金してしまうため、バックアップは残さない)
            #db.collection(ManageCollection).document(_type).collection(
            #    _searchWord
            #).document(twitter_api.lastID).set(tweetDict)
            db.collection(StockCollection).document(_type).collection(
                _searchWord
            ).document(twitter_api.lastID).set(tweetDict)
            db.collection(StockCollection).document(_type).set({"tmp": "hoge"})


def TweetsCollect_Timeline(event, context):
    """
      Collect Tweet at Timeline and add to FireStore
    """
    # attribute {"API_KEY" : Twitter関係のKEY}
    # [FireStore]
    # Twitter--Group--Timeline--TweetID -- {id1:{create_at,text, ...},
    #               --{tweet : lastID}      id2:{create_at,text, ...},...}

    firebaseInit()
    att = event["attributes"]
    db_timeline = db.collection(ManageCollection).document(TimelineDoc)

    lastID = "0"
    try:
        lastID = db_timeline.get().to_dict()["tweets"]
        print("lastID : " + lastID)
    except Exception:
        print("Fail to setting LastID...")
        return

    global twitter_api
    twitter_api = TwitterApi(att)
    twitter_api.setParam_Timeline(lastID)

    tweetDf = getTweets_Timeline()
    tweetDict = reshapeTweets(tweetDf)
    if len(tweetDict) > 0:
        # 最新のIDを更新
        db_timeline.update({"tweets": twitter_api.lastID})

        # FireStoreに追加(使用量が多く課金してしまうため、バックアップは残さない)
        # db_timeline.collection("tweets").document(twitter_api.lastID).set(tweetDict)
        db.collection(StockCollection).document(TimelineDoc).collection(
            "tweets"
        ).document(twitter_api.lastID).set(tweetDict)
        db.collection(StockCollection).document(TimelineDoc).set({"tmp": "hoge"})

