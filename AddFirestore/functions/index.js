'use strict';

const functions = require('firebase-functions');

// The Firebase Admin SDK to access Firestore.
const admin = require('firebase-admin');
admin.initializeApp();

exports.addFireStore = functions
    .region('asia-northeast1')
    .https.onRequest(async (req, res) => {
        const collection = 'testCollection';
        const FieldValue = admin.firestore.FieldValue;
        const serverTime = FieldValue.serverTimestamp();
        var date = new Date();
        var ts = date.getTime();
        ts = Math.floor(ts / 1000);
        const data = req.body.data;

        console.log(serverTime);
        console.log(ts);
        console.log(data);

        await admin.firestore()
            .collection(collection)
            .doc(String(ts))
            .set(
                {
                    ts: ts,
                    serverTime: serverTime,
                    data: data
                }
            );
        res.json({ result: `Message with ID: ${ts} added.` });
    });
