'use strict';

const rcloadenv = require('@google-cloud/rcloadenv');

const line = require('@line/bot-sdk');
var bbt = require('beebotte');

var envConfig;


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

        const config = {
            channelAccessToken: envConfig.CHANNEL_ACCESS_TOKEN,
            channelSecret: envConfig.CHANNEL_SECRET,
        };

        const client = new line.Client(config);

        var clientBeebotte = new bbt.Connector({ apiKey: envConfig.BEEBOTTE_API, secretKey: envConfig.BEEBOTTE_SECRET_KEY });
        var ch = envConfig.BEEBOTTE_CHANNEL;

        client.getGroupMemberProfile(groupId, userId)
            .then((profile) => {
                userName = profile.displayName;
                //console.log('displayName\n' + userName);
                clientBeebotte.writeBulk(
                    {
                        channel: ch, records: [
                            {
                                resource: "message", data: {
                                    "user": userName,
                                    "msg": message
                                }
                            },
                        ]
                    },

                    function (err, res) {
                        if (err) throw (err);
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

exports.handler_Fromline = function echoBot(req, res) {
    rcloadenv.getAndApply('LINE-Config', {})
        .then((env) => {
            envConfig = env;
        })
        .then(() => {
            Promise
                .all(req.body.events.map(handleEvent))
                .then(result => res.status(200).send(`Success: ${result}`))
                .catch(err => res.status(400).send(err.toString()));
        })
        .catch((err) => {
            console.error('ERROR:', err);
        })
};