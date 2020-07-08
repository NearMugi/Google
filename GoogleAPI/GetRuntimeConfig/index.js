//RuntimeConfigを取得
//引数 {"list" : ["リスト名1","リスト名2"] }
//RuntimeConfigの中身ではない。
//リストで受け取り、jsonで返す

//!!!セキュリティを高める!!!
//取得する前に、特定のStorageにアクセスできるかチェックする。
//アクセスできる＝GCPの管理者
const rcloadenv = require('@google-cloud/rcloadenv');
const { Storage } = require('@google-cloud/storage');
const storage = new Storage();

var isAccess;
var reqList;
var retInfo;

function sequenceTasks(tasks) {
    function recordValue(results, value) {
        results.push(value);
        return results;
    }
    var pushValue = recordValue.bind(null, []);
    return tasks.reduce(function (promise, task) {
        return promise.then(task).then(pushValue);
    }, Promise.resolve());
}

var promises = {
    doTask_AccessCheck: function () {
        return accessStorage().then((res) => {
            isAccess = res[1];
            return res[0];  //終了メッセージを返す
        });
    },
    doTask_getList: function () {
        return getList().then();
    },
};


function accessStorage() {
    return new Promise(function (resolve, reject) {
        //Storageにアクセスしてみる
        reqBucket = "watashicheck";
        reqFn = "accessCheck.txt";

        const myBucket = storage.bucket(reqBucket);
        const remoteFile = myBucket.file(reqFn);
        remoteFile.exists().then(function (data) {
            resolve(['accessStorage End', data[0]]);
        });
    });
}

function getList() {
    return new Promise(function (resolve, reject) {
        //もしStorageにアクセス出来ていない場合は何もしない。
        console.log(isAccess);
        if (!isAccess) resolve('getList End');


        var len = reqList.length
        //ループ処理の完了を受け取るPromise
        new Promise(function (res, rej) {

            //ループ処理(再帰的に呼び出し)
            function loop(i) {
                // 非同期処理なのでPromiseを利用
                return new Promise(function (resolve, reject) {

                    // 非同期処理部分
                    setTimeout(function () {
                        rcloadenv.getAndApply(reqList[i], {})
                            .then((env) => {
                                //console.log(env)
                                _data = env
                                retInfo.push(_data)
                                //console.log(retInfo)
                                resolve(i + 1);
                            })
                            .catch((err) => {
                                console.error('ERROR:', err);
                                resolve(len)
                            });
                    }, 100);
                })
                    .then(function (count) {
                        //ループを抜けるかどうかの判定
                        if (count >= len) {
                            //抜ける（外側のPromiseのresolve判定を実行）
                            res();
                        } else {
                            //再帰的に実行
                            loop(count);
                        }
                    });
            }

            //初回実行
            loop(0);

        }).then(function () {
            //ループ処理が終わったらここにくる
            resolve('getList End');
        })



    });
}

function main() {
    return sequenceTasks([
        promises.doTask_AccessCheck,
        promises.doTask_getList,
    ]);
}

exports.handler = (req, res) => {
    reqList = req.body["list"];
    retInfo = []

    main().then(function (value) {
        console.log(value);
        res.send(JSON.stringify(retInfo));
    }).catch(function (error) {
        console.log('\n\n\n+++ Error +++');
        console.log(error);
        res.send(JSON.stringify(retInfo));
    });
};


