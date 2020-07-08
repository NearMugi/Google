//早起きシートの読み書きを行う

var GoogleSpreadsheet = require('google-spreadsheet');
require('date-utils');

const rcloadenv = require('@google-cloud/rcloadenv');
var env;
var doc;

var sheet;
var getData = JSON.stringify({});


var reqTs;
var reqDate;
var reqTime;
var reqUser;

var flgAdd; //追加するかどうか
var rowsPos; //追加する場所
var rank;   //何番目に追加したか

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
    doTask_GetConfig: function () {
        return getenvConfig().then((res) => {
            env = res[1];
            return res[0];  //終了メッセージを返す
        });
    },
    doTask_setAuth: function () {
        return setAuth().then();
    },
    doTask_GetInfo: function () {
        return getInfoAndWorkSheets().then();
    },
    doTask_JdgRireki: function () {
        return workingWithRows().then((res) => {
            flgAdd = res[1];
            rowsPos = res[2];
            rank = res[3];
            return res[0];  //終了メッセージを返す
        });
    },
    doTask_AddCells: function () {
        return workingWithCells().then();
    },

    doTask_GetMsg: function () {
        return getMsg().then();
    },
};

function getenvConfig() {
    return new Promise(function (resolve, reject) {
        rcloadenv.getAndApply('SpreadSheets-Config', {})
            .then((env) => {
                resolve(['getenvConfig End', env]);
            })
            .catch((err) => {
                console.error('ERROR:', err);
            })
    });
}

function setAuth() {
    return new Promise(function (resolve, reject) {
        //不格好だけどPRIVATE_KEYに含まれている改行が上手く処理できなかったので分割した。
        var key = env.PRIVATE_KEY_0 + '\n';
        key += env.PRIVATE_KEY_1 + '\n';
        key += env.PRIVATE_KEY_2 + '\n';
        key += env.PRIVATE_KEY_3 + '\n';
        key += env.PRIVATE_KEY_4 + '\n';
        key += env.PRIVATE_KEY_5 + '\n';
        key += env.PRIVATE_KEY_6 + '\n';
        key += env.PRIVATE_KEY_7 + '\n';
        key += env.PRIVATE_KEY_8 + '\n';
        key += env.PRIVATE_KEY_9 + '\n';
        key += env.PRIVATE_KEY_10 + '\n';
        key += env.PRIVATE_KEY_11 + '\n';
        key += env.PRIVATE_KEY_12 + '\n';
        key += env.PRIVATE_KEY_13 + '\n';
        key += env.PRIVATE_KEY_14 + '\n';
        key += env.PRIVATE_KEY_15 + '\n';
        key += env.PRIVATE_KEY_16 + '\n';
        key += env.PRIVATE_KEY_17 + '\n';
        key += env.PRIVATE_KEY_18 + '\n';
        key += env.PRIVATE_KEY_19 + '\n';
        key += env.PRIVATE_KEY_20 + '\n';
        key += env.PRIVATE_KEY_21 + '\n';
        key += env.PRIVATE_KEY_22 + '\n';
        key += env.PRIVATE_KEY_23 + '\n';
        key += env.PRIVATE_KEY_24 + '\n';
        key += env.PRIVATE_KEY_25 + '\n';
        key += env.PRIVATE_KEY_26 + '\n';
        key += env.PRIVATE_KEY_27;

        var creds_json = {
            client_email: env.CLIENT_EMAIL,
            private_key: key,
        }
        doc = new GoogleSpreadsheet(env.SHEET_ID_WAKEUP);
        doc.useServiceAccountAuth(creds_json, function () {
            resolve('setAuth End');
        });
    });
}

function getInfoAndWorkSheets() {
    return new Promise(function (resolve, reject) {

        doc.getInfo(function (err, info) {
            if (err) throw err;
            console.log('Loaded doc: ' + info.title + ' by ' + info.author.email);
            sheet = info.worksheets[0];
            resolve('getInfoAndWorkSheets End');
        });
    });
}

function workingWithRows() {
    return new Promise(function (resolve, reject) {
        //すでに登録されているかチェックする
        //追加する行と順番も取得する。
        //取得した最終行にヘッダーも含めて＋２にしている。
        sheet.getRows(function (err, rows) {
            if (err) throw err;

            var _flg = true;
            var _rank = 1;
            for (var i in rows) {
                if (rows[i].date == reqDate) {
                    _rank++;
                    if (rows[i].user == reqUser) {
                        _flg = false;
                        break;
                    }
                }
            }
            resolve(['workingWithRows End', _flg, rows.length + 2, _rank]);

        });
    });
}

function workingWithCells() {
    return new Promise(function (resolve, reject) {
        if (!flgAdd) {
            resolve('Not Add User');
        } else {
            sheet.getCells({
                'min-row': rowsPos,
                'max-row': rowsPos,
                'min-col': 1,
                'max-col': 5,
                'return-empty': true
            }, function (err, cells) {
                if (err) throw err;
                // bulk updates make it easy to update many cells at once
                cells[0].value = reqTs;
                cells[1].value = reqDate;
                cells[2].value = reqTime;
                cells[3].value = reqUser;
                cells[4].value = rank;

                sheet.bulkUpdateCells(cells); //async

                //console.log(rowsPos)
                for (var i in cells) {
                    cell = cells[i];
                    console.log(cell.batchId + "\t" + cell.value);
                }

                resolve('workingWithCells End');
            });
        }
    });
}

function getMsg() {
    return new Promise(function (resolve, reject) {
        getData = { "add": flgAdd, "rank": rank };
        resolve('getMsg End');
    });
}

function main() {
    return sequenceTasks([
        promises.doTask_GetConfig,
        promises.doTask_setAuth,
        promises.doTask_GetInfo,
        promises.doTask_JdgRireki,
        promises.doTask_AddCells,
        promises.doTask_GetMsg,
    ]);
}


exports.handler = function ReadAndWriteWakeup(req, res) {

    getData = JSON.stringify({});

    reqTs = req.body["ts"];
    reqDate = req.body["date"];
    reqTime = req.body["time"];
    reqUser = req.body["user"];

    main().then(function (value) {
        console.log(value);
        res.send(getData);
    }).catch(function (error) {
        console.log('\n\n\n+++ Error +++');
        console.log(error);
        res.send(getData);
    });
};