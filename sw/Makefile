
src_dir = $(shell pwd)

bmark = hello_world
iterations = 256

#--------------------------------------------------------------------
# Sources
#--------------------------------------------------------------------

include sources.mk

#--------------------------------------------------------------------
# Build rules
#--------------------------------------------------------------------

RISCV_PREFIX ?= riscv64-unknown-elf-
RISCV_GCC ?= $(RISCV_PREFIX)gcc
RISCV_GCC_OPTS ?= -march=rv64gc -mabi=lp64d -DPREALLOCATE=1 -DREPEAT_FACTOR=$(iterations) -mcmodel=medany -static -std=gnu99 -O2 -ffast-math -fno-common -Wno-implicit -fno-builtin-printf -fno-tree-loop-distribute-patterns
RISCV_LINK_OPTS ?= -static -nostdlib -nostartfiles -lm -lgcc -T $(src_dir)/common/test.ld
RISCV_OBJDUMP ?= $(RISCV_PREFIX)objdump --disassemble-all --disassemble-zeroes --section=.text --section=.text.startup --section=.text.init
RISCV_SIM ?= spike --isa=rv64gc

incs  += -I$(src_dir)/../env -I$(src_dir)/common $(addprefix -I$(src_dir)/, $(bmark))

define compile_template
build/$(1)/$(1).riscv: $(wildcard $(src_dir)/$(1)/*) $(wildcard $(src_dir)/common/*)
	mkdir -p build/$(1)
	$$(RISCV_GCC) $$(incs) $$(RISCV_GCC_OPTS) -o $$@ $(wildcard $(src_dir)/$(1)/*.c) $(wildcard $(src_dir)/$(1)/*.S) $(wildcard $(src_dir)/common/*.c) $(wildcard $(src_dir)/common/*.S) $$(RISCV_LINK_OPTS)
endef

$(foreach bmark,$(__bmarks),$(eval $(call compile_template,$(bmark))))

#------------------------------------------------------------
# Special case: attacks payload

ifneq ($(filter $(bmark),$(__jop_attacks)),)
    RISCV_GCC_OPTS = -mabi=lp64d -march=rv64gc -DWIDTH=64 -mcmodel=medany -fno-stack-protector -z execstack -no-pie
endif

#------------------------------------------------------------
# Build and run benchmarks on Spike

build_dir = build/$(bmark)

bmark_riscv_bin  = $(addprefix $(build_dir)/, $(addsuffix .riscv,      $(bmark)))
bmark_riscv_dump = $(addprefix $(build_dir)/, $(addsuffix .riscv.dump, $(bmark)))
bmark_riscv_out  = $(addprefix $(build_dir)/, $(addsuffix .riscv.out,  $(bmark)))
bmark_riscv_log  = $(addprefix $(build_dir)/, $(addsuffix .riscv.log,  $(bmark)))

$(bmark_riscv_dump): %.riscv.dump: %.riscv
	$(RISCV_OBJDUMP) $< > $@

$(bmark_riscv_out): %.riscv.out: %.riscv
	$(RISCV_SIM) -l --log-commits --log=$(bmark_riscv_log) $< > $@

riscv: $(bmark_riscv_dump)
run: $(bmark_riscv_out)

#------------------------------------------------------------
# Default

all: riscv run

#------------------------------------------------------------
# Housekeeping

clean:
	rm -rf build