bmarks = hello_world
waves = 0

ip = jop_alarm
__test = test_$(ip)_ip

__comma = ,
__split= $(foreach v,$(1),$(call __process,$(v)))
__process = $(subst $(__comma), ,$(1))
__split_bmarks := $(call __split,$(subst ,, ,$(bmarks)))

$(__split_bmarks):
	$(MAKE) -i -C sw all bmark=$@

run: $(__split_bmarks)
	ASPYCOT_BMARKS=$(bmarks) \
	ASPYCOT_WAVES=$(waves) \
	pytest tb/entry.py::$(__test) -vvv -s

clean:
	$(MAKE) -C sw clean
