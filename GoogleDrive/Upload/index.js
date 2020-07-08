//Driveへアップロード
//https://developers.google.com/drive/api/v3/manage-uploads
//https://developers.google.com/drive/api/v3/reference/files/create
var fs = require('fs');
const { google } = require('googleapis');
const rcloadenv = require('@google-cloud/rcloadenv');

var _refresh_token;
var _client_id;
var _client_secret;

var reqBinary;
var reqFn;
var reqMineType;
var reqParentID;
var reqComment;

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
    doTask_CreateTmpFile: function () {
        return createTmpFile().then((res) => {
            return res[0];  //
        });
    },
    doTask_Upload: function () {
        return upload().then((res) => {
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

function createTmpFile() {
    return new Promise(function (resolve, reject) {
        //仮のファイルを作成
        fs.writeFile('/tmp/hoge.jpeg', reqBinary, function (err) {
            if (err) {
                resolve(['createTmpFile Error']);
            }
            resolve(['createTmpFile End']);
        });

    });
}

function upload() {
    return new Promise(function (resolve, reject) {

        var oauth2Client = new google.auth.OAuth2(
            _client_id,
            _client_secret
        );
        oauth2Client.setCredentials({
            refresh_token: _refresh_token
        });

        var fileMetadata = {
            'name': reqFn,
            'parents': [reqParentID],
            'description': reqComment
        };

        var media = {
            mimeType: reqMineType,
            body: fs.createReadStream('/tmp/hoge.jpeg')
        };

        //console.log(media)
        console.log(fileMetadata)

        var drive = google.drive({ version: 'v3', auth: oauth2Client });

        drive.files.create({
            resource: fileMetadata,
            media: media,
            fields: 'id'
        }, function (err, file) {
            if (err) {
                // Handle error
                console.error(err);
                resolve(['upload Error']);
            } else {
                //console.log('File Id: ', file.id);
                resolve(['upload End']);
            }
        });

    });
}

function main() {
    return sequenceTasks([
        promises.doTask_GetInfo,
        promises.doTask_CreateTmpFile,
        promises.doTask_Upload,
    ]);
}

exports.handler = (req, res) => {
    reqFn = req.body["fn"];
    reqParentID = req.body["parentID"];
    reqMineType = req.body["mineType"];
    reqBinary = req.body["binary"]["data"];
    reqComment = req.body["comment"];
    reqBinary = new Buffer(reqBinary);
    //console.log(reqBinary)

    main().then(function (value) {
        console.log(value);
        res.send({ 'ret': 'end' });
    }).catch(function (error) {
        console.log(error);
        res.send({ 'ret': 'error' });
    });




};

