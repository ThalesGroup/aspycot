# Aspycot: A Spike and Python CO-Simulation Testbench for Hardware Monitoring IPs

## Introduction

Aspycot is a platform allowing rapid prototyping and early-validation of hardware monitoring IPs in standalone mode.
It automates the compiling of applications and uses an instruction set simulator (ISS) to get execution traces.
The traces are used as input stimuli for the hardware IP, whose behavior is checked in respect to a certain execution (or threat) model.

Aspycot is based on components from the open source ecosystem:

- RISC-V gcc toolchain
- Spike RISC-V ISS
- cocotb

## Get started

You need the following tools:

- [A RISC-V compiler](https://github.com/riscv-collab/riscv-gnu-toolchain)
- [Spike ISS](https://github.com/riscv-software-src/riscv-isa-sim)
- [cocotb](https://www.cocotb.org/) (currently aspycot used cocotb 1.9.2)
- a HDL simulator [supported by cocotb](https://docs.cocotb.org/en/stable/simulator_support.html) (verilator for Verilog/SystemVerilog, GHDL for VHDL ...)
- [pytest](https://docs.pytest.org/en/stable/)

And then you can use the platform with the example from the [associated article](README.md#publication):

```bash
git clone aspycot
make ip=jop_alarm bmarks=hello_world,jop10
```

## Documentation

Documentation is available at [docs](docs/) on how to extend the platform with new applications, threat models or IPs.

## Contributing

If you are interested in contributing to Aspycot, start by reading the [Contributing guide](/CONTRIBUTING.md).

## License

The License is GPLv3. See [LICENSE](/LICENSE.md) for more information.

## Publication

Aspycot was presented in RAPIDO'25 workshop and the article will soon be available on ACM.
