'use strict';

require('dotenv').config();
const line = require('@line/bot-sdk');
var bbt = require('beebotte');

const config = {
    channelAccessToken: process.env.CHANNEL_ACCESS_TOKEN,
    channelSecret: process.env.CHANNEL_SECRET,
};

const client = new line.Client(config);

var clientBeebotte = new bbt.Connector({apiKey: process.env.BEEBOTTE_API, secretKey: process.env.BEEBOTTE_SECRET_KEY});
var ch = process.env.BEEBOTTE_CHANNEL;
var user = process.env.BEEBOTTE_RESOURCE_USER;
var msg = process.env.BEEBOTTE_RESOURCE_MSG;
var gId = process.env.BEEBOTTE_RESOURCE_GROUPID;

function handleEvent(event) {
    console.log('[handleEvent]\n' + event);

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
            return false;
        }

        client.getGroupMemberProfile(groupId, userId)
            .then((profile) => {
                userName = profile.displayName;
                //console.log('displayName\n' + userName);

				clientBeebotte.write(
                    {channel: ch, resource: gId, data: groupId },
					function(err, res) {
						if(err) throw(err);
                        console.log(res);
				});


                clientBeebotte.publishBulk(
                    {
                        channel: ch, records: [
                            { resource: user, data: userName },
                            { resource: msg, data: message }
                        ]
                    },

					function(err, res) {
						if(err) throw(err);
                        console.log(res);
				});
                
            })
            .then(() => {
                return true;
            })
            .catch((err) => {
                // error handling
                console.log(err);
	            return false;
            });

    }
}

exports.handler = function echoBot(req, res) {
    Promise
        .all(req.body.events.map(handleEvent))
        .then(result => res.status(200).send(`Success: ${result}`))
        .catch(err => res.status(400).send(err.toString()));
};
