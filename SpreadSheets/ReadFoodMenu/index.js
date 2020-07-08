//保育園のメニューを取得する

var GoogleSpreadsheet = require('google-spreadsheet');
require('date-utils');

const rcloadenv = require('@google-cloud/rcloadenv');
var env;
var doc;

var sheet;
var targetDate = 0;
var getData = JSON.stringify({});

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
        return workingWithRows().then();
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
        doc = new GoogleSpreadsheet(env.SHEET_ID_FOODMENU);
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

        sheet.getRows({
            offset: targetDate,
            limit: targetDate + 1,
        }, function (err, rows) {
            if (err) throw err;
            console.log(rows[0]);
            getData = JSON.stringify({
                "date": rows[0].date,
                "lunch": [rows[0].lunch1, rows[0].lunch2, rows[0].lunch3, rows[0].lunch4, rows[0].lunch5],
                "snack": [rows[0].snack1, rows[0].snack2],
                "addfood": [rows[0].addfood1, rows[0].addfood2]
            });

            resolve('workingWithRows End');
        });
    });
}

function main() {
    return sequenceTasks([
        promises.doTask_GetConfig,
        promises.doTask_setAuth,
        promises.doTask_GetInfo,
        promises.doTask_GetRows,
    ]);
}


exports.handler = function AccessSpreadSheet(req, res) {

    getData = JSON.stringify({});
    targetDate = 0;
    if (req.body.date != undefined) {
        targetDate = parseInt(req.body.date, 10);
    }
    if (targetDate <= 0 || targetDate > 31) {
        console.log('TargetDate is incorrect');
        res.send(getData);
        process.exit();
    }
    console.log('Target Date:' + targetDate);


    main().then(function (value) {
        console.log(value);
        res.send(getData);
    }).catch(function (error) {
        console.log('\n\n\n+++ Error +++');
        console.log(error);
        res.send(getData);
    });
};