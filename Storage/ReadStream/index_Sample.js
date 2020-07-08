//.on('data'~  )は以下のURLを参考にした
//https://qiita.com/koshilife/items/634799bb57872ce0a169

const { Storage } = require('@google-cloud/storage');
const storage = new Storage();

const bucketName = ''
const srcFilename = ''

const myBucket = storage.bucket(bucketName);

const remoteFile = myBucket.file(srcFilename);

remoteFile.createReadStream()
    .on('error', function (err) { console.log(err) })
    .on('response', function (response) {
        console.log('Server connected and responded with the specified status and headers.');
        //console.log(response);
    })
    .on('end', function () {
        console.log('The file is fully downloaded.');
    })
    .on('data', function (data) {
        console.log(data);
        console.log(data.toString());
    });
