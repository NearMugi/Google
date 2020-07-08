// Imports the Google Cloud client library
const { Storage } = require('@google-cloud/storage');

// Creates a client
const storage = new Storage();

/**
 * TODO(developer): Uncomment the following lines before running the sample.
 */
const bucketName = '' //'Name of a bucket, e.g. my-bucket';
const srcFilename = '' //'Remote file to download, e.g. file.txt';
const destFilename = './hoge.txt' //'Local destination for file, e.g. ./local/path/to/file.txt';

const options = {
    // The path to which the file should be downloaded, e.g. "./file.txt"
    destination: destFilename,
};


async function main() {
    await storage
        .bucket(bucketName)
        .file(srcFilename)
        .download(options);
    console.log(
        `gs://${bucketName}/${srcFilename} downloaded to ${destFilename}.`
    );

}

main();


