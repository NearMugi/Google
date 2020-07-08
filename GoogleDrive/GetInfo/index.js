//Driveの単一ファイル情報を取得
//ファイルの入っているフォルダIDとファイル名を指定。
//複数ファイル(例えばフォルダ内全て)の取得には対応していない。
//https://developers.google.com/drive/api/v3/search-parameters

var fs = require('fs');
const { google } = require('googleapis');
const rcloadenv = require('@google-cloud/rcloadenv');

var _refresh_token;
var _client_id;
var _client_secret;

var reqParent;
var reqFn;

var retInfo = {};

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
    doTask_GetInfo: function () {
        return getInfo().then((res) => {
            return res[0];  //
        });
    },
    doTask_list: function () {
        return list().then((res) => {
            return res[0];  //
        });
    },
};

function getInfo() {
    return new Promise(function (resolve, reject) {
        rcloadenv.getAndApply('googleAPI', {})
            .then((env) => {
                _refresh_token = env.refreshToken;
                _client_id = env.clientID;
                _client_secret = env.clientSecret;
                resolve(['getInfo End']);
            })
            .catch((err) => {
                console.error('ERROR:', err);
                resolve(['getInfo Error']);
            })

    });
}

function list() {
    return new Promise(function (resolve, reject) {

        var oauth2Client = new google.auth.OAuth2(
            _client_id,
            _client_secret
        );
        oauth2Client.setCredentials({
            refresh_token: _refresh_token
        });

        var drive = google.drive({ version: 'v3', auth: oauth2Client });

        var _q = "parents in '" + reqParent + "'";
        _q += " and ";
        _q += "name='" + reqFn + "'"

        //console.log(_q)

        drive.files.list({
            q: _q,
            spaces: "drive",
            fields: "files(id, name, parents, mimeType)"
        }, function (err, res) {
            if (err) {
                // Handle error
                console.error(err);
                resolve(['list err']);
            } else {
                _info = res.data.files[0]
                //console.log(_info)
                retInfo = {
                    id: _info.id,
                    mimeType: _info.mimeType,
                    name: _info.name,
                    parentID: _info.parents[0]
                }
                //console.log(retInfo)
                resolve(['list End']);
            }
        });

    });
}

function main() {
    return sequenceTasks([
        promises.doTask_GetInfo,
        promises.doTask_list,
    ]);
}

exports.handler = (req, res) => {
    reqParent = req.body["parentID"];
    reqFn = req.body["fn"];

    main().then(function (value) {
        console.log(value);
        res.send(retInfo);
    }).catch(function (error) {
        console.log(error);
        retInfo = {
            err: error
        }
        res.send(retInfo);
    });
};

