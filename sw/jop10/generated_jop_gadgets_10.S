# List of gadgets

.globl gadget6
gadget6:
sd a0, 24(sp)
addi a1, sp, 24
jr s0

.globl gadget2
gadget2:
jr s0

.globl gadget3
gadget3:
li a2, 0
jr s0

.globl syscall
syscall:
li a7, 93
ecall

.globl gadget7
gadget7:
jr s0

.globl gadget5
gadget5:
addi a0, sp, 24
jr s0

.globl gadget4
gadget4:
jr s0

.globl gadget1
gadget1:
mv a4, a3
nop
slti a3, a0, 96
jr s0

.globl init
init:
ld s0, 0(sp)
mv s2, sp
addi s2, s2, 8
jr s0

.globl dispatcher
dispatcher:
ld s1, 0(s2)
addi s2, s2, 8
jr s1

