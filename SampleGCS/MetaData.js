// Imports the Google Cloud client library
const Storage = require('@google-cloud/storage');

// Creates a client
const storage = new Storage();

const bucketName = "[PROJECT_ID].appspot.com";
const bucket = storage.bucket(bucketName);
const files = bucket.getFiles();

//Get File objects for the files currently in the bucket as a readable object stream.
bucket.getFilesStream()
	.on('error', console.error)
	.on('data', function (file) {
		// file is a File object.
		console.log(`File: ${file.name}`);

		file.getMetadata().then(function (data) {
			const metaData = data[0];
			const apiResponse = data[1];
			console.log("+++++++++metaData++++++++++");
			console.log(metaData);
			console.log("+++++++++apiResponse++++++++++");
			console.log(apiResponse);
			console.log("");
		});
	})
	.on('end', function () {
		// All files retrieved.
	});


