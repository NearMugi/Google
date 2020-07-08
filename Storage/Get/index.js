const { Storage } = require('@google-cloud/storage');
const storage = new Storage();

const bucketName = ''
const srcFilename = ''

const myBucket = storage.bucket(bucketName);

const file = myBucket.file(srcFilename);


//-
// If the callback is omitted, we'll return a Promise.
//-
file.get().then(function (data) {
    const file = data[0];
    const apiResponse = data[1];
    //console.log(apiResponse);
    //console.log(file);

});

file.getMetadata().then(function (data) {
    const metadata = data[0];
    const apiResponse = data[1];
    console.log(metadata);
});