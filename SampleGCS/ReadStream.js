// Imports the Google Cloud client library
const Storage = require('@google-cloud/storage');

// Creates a client
const storage = new Storage();

const bucketName = "[PROJECT_ID].appspot.com";
const bucket = storage.bucket(bucketName);
const remoteFile = bucket.file('TestJson.json');
const fileReaderStream = remoteFile.createReadStream();
fileReaderStream.setEncoding('utf8');

fileReaderStream
	.on('error', function (err) { })
	.on('data', function (data) {
		console.log(data);
	})
	.on('response', function (response) {
		// Server connected and responded with the specified status and headers.
	})
	.on('end', function () { console.log('+++ Data End +++') });


fileReaderStream.resume();
