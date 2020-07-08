'use strict';

require('dotenv').config();
const line = require('@line/bot-sdk');

const config = {
    channelAccessToken: process.env.CHANNEL_ACCESS_TOKEN,
    channelSecret: process.env.CHANNEL_SECRET,
};

const client = new line.Client(config);

function handleEvent(event) {
    console.log(event);

    var message = '';
    var groupId = '';
    var userId = '';
    var userName = '';
    if (event.type === 'message' && event.message.type === 'text') {
        message = event.message.text;
        groupId = event.source.groupId;
        userId = event.source.userId;

        if (groupId == undefined) {
            console.log('[WARNING]Missing groupId');
            return;
        }

        client.getGroupMemberProfile(groupId, userId)
            .then((profile) => {
                userName = profile.displayName;
                console.log('displayName\n' + profile.displayName);
                const echo = { type: 'text', text: userName + "\n" + message };
                return client.replyMessage(event.replyToken, echo);
            })
            .catch((err) => {
                // error handling
                console.log(err);
            });

    }
}

exports.handler = function echoBot(req, res) {
    Promise
        .all(req.body.events.map(handleEvent))
        .then(result => res.status(200).send(`Success: ${result}`))
        .catch(err => res.status(400).send(err.toString()));
};
