const rcloadenv = require('@google-cloud/rcloadenv');

var ret_access_token;
var _refresh_token;
var _client_id;
var _client_secret;

function sequenceTasks(tasks) {
  function recordValue(results, value) {
      results.push(value);
      return results;
  }
  var pushValue = recordValue.bind(null, []);
  return tasks.reduce(function (promise, task) {
      return promise.then(task).then(pushValue);
  }, Promise.resolve());
}

var promises = {
  doTask_GetInfo: function () {
    return getInfo().then((res) => {
      return res[0];  //
    });
  },
  doTask_GetAccessToken: function () {
    return getAccessToken().then((res) => {
      return res[0];  //
    });
  },
};

function getInfo() {
  return new Promise(function (resolve, reject) {
    rcloadenv.getAndApply('googleAPI', {})
      .then((env) => {
        _refresh_token = env.refreshToken;
        _client_id = env.clientID;
        _client_secret = env.clientSecret;
        resolve(['getInfo End']);
      })
      .catch((err) => {
        console.error('ERROR:', err);
        resolve(['getInfo Error']);
      })

  });
}

function getAccessToken() {
  return new Promise(function (resolve, reject) {
    let body = JSON.stringify({
      refresh_token: _refresh_token,
      client_id: _client_id,
      client_secret: _client_secret,
      grant_type: 'refresh_token'
    });


    var options = {
      host: 'www.googleapis.com',
      port: 443,
      path: '/oauth2/v4/token',
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Content-Length': body.length
      }
    };

    var https = require('https');
    let req = https.request(options, (res) => {
      console.log(res.statusCode);
      res.setEncoding('utf8');
      res.on('data', (chunk) => {
        tmp = JSON.parse(chunk);
        console.log(tmp);
        ret_access_token = tmp.access_token;
        resolve(['getAccessToken End']);
      });
    });
    req.on('error', (e) => {
      console.log('problem with request: ' + e.message);
      resolve(['getAccessToken Error']);
    });

    req.write(body);
    req.end();

  });
}

function main() {
  return sequenceTasks([
    promises.doTask_GetInfo,
    promises.doTask_GetAccessToken,
  ]);
}

exports.handler = function WriteCatWatching(req, res) {
  ret_access_token = 'HOGE';

  main().then(function (value) {
    console.log(value);
    res.send(ret_access_token);
  }).catch(function (error) {
    console.log('\n\n\n+++ Error +++');
    console.log(error);
    res.send(ret_access_token);
  });
};

