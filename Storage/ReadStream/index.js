//CloudFunctionsでStorageのデータを取得する

const { Storage } = require('@google-cloud/storage');
const storage = new Storage();

exports.handler = (req, res) => {

    var getData = new Buffer('');
    var totalSize = 0;

    var tmpData = new Buffer('');
    var tmpSize = 0;

    reqBucket = req.body["bucket"];
    reqFn = req.body["fn"];

    const myBucket = storage.bucket(reqBucket);
    const remoteFile = myBucket.file(reqFn);

    remoteFile.createReadStream()
        .on('error', function (err) {
            console.log('[ERROR]' + err);
            res.send({ "data": getData, "err": true });
        })
        .on('response', function (response) {
            console.log('Server connected and responded with the specified status and headers.');
            //console.log(response);
        })
        .on('end', function () {
            console.log('The file is fully downloaded.  Size:' + totalSize);
            //残っているtmpDataを結合する
            getData = Buffer.concat([getData, tmpData]);
            //console.log(getData);
            //console.log(getData.toString());
            res.send({ "data": getData, "err": false });
        })
        .on('data', function (data) {
            //console.log('Get Data  Size:' + Buffer.byteLength(data));
            //console.log(data);
            //console.log(data.toString());
            //console.log(new Buffer(data, 'base64'));
            totalSize += Buffer.byteLength(data);
            tmpSize += Buffer.byteLength(data);
            //console.log('TotalSize:' + Buffer.byteLength(getData));

            //10MB(10485760byte)を超えた場合はエラー
            if (totalSize > 10485760) {
                console.log('[ERROR] Size Over :' + totalSize);
                res.send({ "data": "Size Over", "err": true });
            } else {
                tmpData = Buffer.concat([tmpData, data]);
                //1MBずつ結合する(毎回やると処理が重いため)
                if (tmpSize > 1048576) {
                    getData = Buffer.concat([getData, tmpData]);
                    tmpData = new Buffer('');
                    tmpSize = 0;
                }
            }
        });

};

