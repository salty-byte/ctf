# HITCON CTF 2023 Writeup

HITCON CTF 2023（<https://ctftime.org/event/2019/>）に参加しました。  
金, 08 9月 2023, 23:00 JST — 日, 10 9月 2023, 23:00 JST

チーム：OnePaddingで参加しました。
今回も問題を解けなかったので、例のごとく復習していきます。

<!-- @import "[TOC]" {cmd="toc" depthFrom=2 depthTo=3 orderedList=false} -->

<!-- code_chunk_output -->

- [crypto/Share](#cryptoshare)
- [web/Login System](#weblogin-system)

<!-- /code_chunk_output -->

## crypto/Share

47 solves / 222 points

web問が解けそうになかったので、crypto問を少し見てました。（解けてはいないです。）

- 問題コード

```python
#!/usr/bin/env python3
from Crypto.Util.number import isPrime, getRandomRange, bytes_to_long
from typing import List
import os, signal


class SecretSharing:
    def __init__(self, p: int, n: int, secret: int):
        self.p = p
        self.n = n
        self.poly = [secret] + [getRandomRange(0, self.p - 1) for _ in range(n - 1)]

    def evaluate(self, x: int) -> int:
        return (
            sum([self.poly[i] * pow(x, i, self.p) for i in range(len(self.poly))])
            % self.p
        )

    def get_shares(self) -> List[int]:
        return [self.evaluate(i + 1) for i in range(self.n)]


if __name__ == "__main__":
    signal.alarm(30)
    secret = bytes_to_long(os.urandom(32))
    while True:
        p = int(input("p = "))
        n = int(input("n = "))
        if isPrime(p) and int(13.37) < n < p:
            shares = SecretSharing(p, n, secret).get_shares()
            print("shares =", shares[:-1])
        else:
            break
    if int(input("secret = ")) == secret:
        print(open("flag.txt", "r").read().strip())
```

p（素数）とn（整数）を入力すると、sharesが出力される。  
範囲は13.37 < n < p である必要がある。  
sharesによって、ランダムに生成されるsecretの値を推測できればフラグがもらえる。

- shareの計算
  - 以下のようなP(x)の値が返される。x=1...n-1で計n-1個。
  - aはランダムに生成される整数。範囲は、0 <= a < p-1。

```math
P(x) = secret + a_1x^1 + a_2x^2 + ... + a_{n-1}x^{n-1} \quad (mod \, p)
```

- n = 14の場合

```math
\begin{cases}
  P(1) = secret + a_1 + a_2 + ... + a_{13} \quad (mod \, p)\\
  P(2) = secret + 2a_1 + 2^2a_2 + ... + 2^{13}a_{13} \quad (mod \, p)\\
  ... \\
  P(13) = secret + 13a_1 + 13^2a_2 + ... + 13^{13}a_{13} \quad (mod \, p)
\end{cases}
```

// TODO

## web/Login System

7 solves / 360 points

// TODO
