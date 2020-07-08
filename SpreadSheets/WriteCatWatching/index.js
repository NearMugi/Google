//キャットタワーの記録

var GoogleSpreadsheet = require('google-spreadsheet');
require('date-utils');

const rcloadenv = require('@google-cloud/rcloadenv');
var env;
var doc;

var sheet;
var getData = JSON.stringify({});
var rowsPos = 0; //追加する場所

var reqDate;
var reqTime;
var reqfind;
var reqy0;
var reqy1;
var reqy2;
var reqy3;

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
    doTask_GetRows: function () {
        return workingWithRows().then((res) => {
            rowsPos = res[1];
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
        doc = new GoogleSpreadsheet(env.SHEET_ID_CATWATCHING);
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
        sheet.getRows(function (err, rows) {
            if (err) throw err;
            resolve(['workingWithRows End', rows.length + 2]);
        });
    });
}

function workingWithCells() {
    return new Promise(function (resolve, reject) {
        console.log('AddRowPos : ' + rowsPos)
        sheet.getCells({
            'min-row': rowsPos,
            'max-row': rowsPos,
            'min-col': 1,
            'max-col': 7,
            'return-empty': true
        }, function (err, cells) {
            if (err) throw err;
            // bulk updates make it easy to update many cells at once
            cells[0].value = reqDate;
            cells[1].value = String(('0000000000' + reqTime).slice(-6)); //ゼロ埋め
            cells[2].value = String(reqfind); //なぜか0が代入できないので文字に変換
            cells[3].value = reqy0;
            cells[4].value = reqy1;
            cells[5].value = reqy2;
            cells[6].value = reqy3;

            sheet.bulkUpdateCells(cells); //async
            resolve('workingWithCells End');
        });
    });
}

function getMsg() {
    return new Promise(function (resolve, reject) {
        getData = { "addRowPos": rowsPos };
        resolve('getMsg End');
    });
}

function main() {
    return sequenceTasks([
        promises.doTask_GetConfig,
        promises.doTask_setAuth,
        promises.doTask_GetInfo,
        promises.doTask_GetRows,
        promises.doTask_AddCells,
        promises.doTask_GetMsg,
    ]);
}


exports.handler = function WriteCatWatching(req, res) {
    getData = JSON.stringify({});

    reqDate = req.body["date"];
    reqTime = req.body["time"];
    reqfind = Number(req.body["y"]["find"]);
    reqy0 = Number(req.body["y"]["0"]);
    reqy1 = Number(req.body["y"]["1"]);
    reqy2 = Number(req.body["y"]["2"]);
    reqy3 = Number(req.body["y"]["3"]);
    console.log("[InputData] " + 
        reqDate + "\t" +
        reqTime + "\t" +
        reqfind + "\t" +
        reqy0 + "\t" +
        reqy1 + "\t" +
        reqy2 + "\t" +
        reqy3
    )

    main().then(function (value) {
        console.log(value);
        res.send(getData);
    }).catch(function (error) {
        console.log('\n\n\n+++ Error +++');
        console.log(error);
        res.send(getData);
    });
};