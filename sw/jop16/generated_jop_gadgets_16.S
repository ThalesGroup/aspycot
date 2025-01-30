# List of gadgets

.globl gadget9
gadget9:
addi a0, sp, 24
jr s0

.globl gadget8
gadget8:
jr s0

.globl gadget3
gadget3:
jr s0

.globl syscall
syscall:
li a7, 93
ecall

.globl gadget1
gadget1:
mv a4, a3
nop
slti a3, a0, 96
jr s0

.globl gadget4
gadget4:
jr s0

.globl dispatcher
dispatcher:
ld s1, 0(s2)
addi s2, s2, 8
jr s1

.globl gadget7
gadget7:
mv a3, a3
sub a3, a7, a3
xor a4, a6, a3
jr s0

.globl gadget6
gadget6:
addi a2, a2, -1
jr s0

.globl gadget10
gadget10:
sd a0, 24(sp)
addi a1, sp, 24
jr s0

.globl init
init:
ld s0, 0(sp)
mv s2, sp
addi s2, s2, 8
jr s0

.globl gadget5
gadget5:
li a2, 3
jr s0

.globl gadget11
gadget11:
sub a4, a6, a5
slti a3, a1, 111
jr s0

.globl gadget2
gadget2:
jr s0

