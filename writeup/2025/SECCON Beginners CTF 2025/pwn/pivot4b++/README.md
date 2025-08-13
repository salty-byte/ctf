# pivot4b++

496 Points / 25 Solves

## 調査

```sh
$ file chall
chall: ELF 64-bit LSB pie executable, x86-64, version 1 (SYSV), dynamically linked, interpreter /lib64/ld-linux-x86-64.so.2, BuildID[sha1]=c117241b345cf6b136546d052341f970eb1e9334, for GNU/Linux 4.4.0, not stripped
```

```sh
$ checksec chall
[*] '/home/salt/ctf/writeup/2025/SECCON Beginners CTF 2025/pwn/pivot4b++/chall'
    Arch:       amd64-64-little
    RELRO:      Full RELRO
    Stack:      No canary found
    NX:         NX enabled
    PIE:        PIE enabled
    Stripped:   No
```

```sh
objdump -d -M intel chall > chall.txt
```

- [src.c](./src.c)

```c
#include <stdio.h>
#include <unistd.h>

int vuln() {
 char message[0x30];

 printf("Welcome to the second pivot game!\n");

 printf("> ");
 read(0, message, sizeof(message) + 0x10);

 printf("Message: %s\n", message);

 return 0;
}

int main() {
 setvbuf(stdin, NULL, _IONBF, 0);
 setvbuf(stdout, NULL, _IONBF, 0);
 alarm(120);

 vuln();
}
```

- [pivot4b](../pivot4b++/)と同様に自明なバッファオーバーフローの脆弱性がある

- PIEが有効なため、まずはPIEのベースアドレスをリークさせることを考える

- PIEのベースアドレスがリーク出来たら、libcのベースアドレスをリークさせる

- libcのベースアドレスがリーク出来たら、one gadget等でシェルを実行する

## 実行

```py
python solve.py
```
