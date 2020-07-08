//Driveからダウンロード
var fs = require('fs');
const { google } = require('googleapis');
const rcloadenv = require('@google-cloud/rcloadenv');

var _refresh_token;
var _client_id;
var _client_secret;

var reqFileID;
var reqPath;
var reqFn;

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
    doTask_Download: function () {
        return download().then((res) => {
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

function download() {
    return new Promise(function (resolve, reject) {

        var oauth2Client = new google.auth.OAuth2(
            _client_id,
            _client_secret
        );
        oauth2Client.setCredentials({
            refresh_token: _refresh_token
        });

        var drive = google.drive({ version: 'v3', auth: oauth2Client });
        var dest = fs.createWriteStream(reqPath + '/' + reqFn);
        drive.files.get({ fileId: reqFileID, alt: 'media' }, { responseType: 'stream' },
            function (err, res) {
                res.data
                    .on('end', () => {
                        console.log('Download');
                        resolve(['download End']);
                    })
                    .on('error', err => {
                        console.log('Error', err);
                        resolve(['download Error']);
                    })
                    .pipe(dest);
            }
        );

    });
}

function main() {
    return sequenceTasks([
        promises.doTask_GetInfo,
        promises.doTask_Download,
    ]);
}

exports.handler = (req, res) => {
    reqFileID = req.body["fileID"];
    reqPath = req.body["path"];
    reqFn = req.body["fn"];

    main().then(function (value) {
        console.log(value);
        res.send({ 'ret': 'end' });
    }).catch(function (error) {
        console.log(error);
        res.send({ 'ret': 'error' });
    });




};

