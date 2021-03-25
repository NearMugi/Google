# CloudFunctionsからFireStoreへデータ追加  

## 手順

以下のサイトに従って環境作ればOK  
[はじめに: 最初の関数の記述、テスト、デプロイ  |  Firebase](https://firebase.google.com/docs/functions/get-started?hl=ja)


ポイントとしては、npmのインストールはfunctionsフォルダ内で行うこと
```sh
npm install firebase-functions@latest firebase-admin@latest --save
npm install -g firebase-tools
```

デプロイは以下のコマンド
``` sh
firebase deploy --only functions
```


## TIPS

### [Firebaseコマンドが実行出来ない場合の対処法](https://qiita.com/ebichan_88/items/e3e30461ad4ddd9368f5)

これが出た時

``` sh
$ firebase login 
-bash: firebase: command not found
```

functionフォルダでeslintをインストール

``` sh
eslint --init
```

### [npm install -g に失敗した時の解決](https://qiita.com/rakuraku0615/items/4d47dc6315f01667027a)

使用するユーザーに設定用ディレクトリを作成する

```sh
mkdir ~/.npm-global 
npm config set prefix '~/.npm-global' 
echo ' export PATH=~/.npm-global/bin:$PATH' >> ~/.bash_profile 
source ~/.bash_profile
```

### [ESlint module.exports が no-undef なエラーになるとき](https://chaika.hatenablog.com/entry/2020/04/13/130000)

firebase deploy --only functions したとき、これが出た時  
``` sh
error  'module' is not defined       no-undef
```
.eslintrc.js に "node" : true, が必要

``` js
// .eslintrc.js 
"env": { 
  "browser": true, 
  "es6": true, 
  "node": true, // <- 追加 
},
```
### [関数のリージョンを変更する](https://firebase.google.com/docs/functions/manage-functions?hl=ja#modify-region)

``` js
exports.webhookAsia = functions 
    .region('asia-northeast1') 
    .https.onRequest((req, res) => { 
            res.send("Hello"); 
    });
```

### [サーバーのタイムスタンプ](https://firebase.google.cn/docs/firestore/manage-data/add-data?hl=ja#node.js_7)

``` js
// Get the `FieldValue` object 
const FieldValue = admin.firestore.FieldValue; 
// Create a document reference 
const docRef = db.collection('objects').doc('some-id'); 
// Update the timestamp field with the value from the server 
const res = await docRef.update({ 
  timestamp: FieldValue.serverTimestamp() 
});
```

### 普通のタイムスタンプ

``` js
var date = new Date(); 
var ts = date.getTime(); 
ts = Math.floor(ts / 1000);
```
