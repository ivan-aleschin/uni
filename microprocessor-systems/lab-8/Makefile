CC       = riscv32-none-elf-gcc
OBJCOPY  = riscv32-none-elf-objcopy
OBJDUMP  = riscv32-none-elf-objdump

ARCH     = -march=rv32i_zicsr -mabi=ilp32
CFLAGS   = $(ARCH) -O2 -ffreestanding -nostdlib -Wall
LDFLAGS  = $(ARCH) -Wl,--gc-sections -nostartfiles -T linker_script.ld

# Исходники
SRC_S    = startup.S
SRC_C    = main.c
OBJ      = startup.o main.o

# SystemVerilog: подтягиваем общие файлы из lab-6
LAB6     = ../lab-6
SV_COMMON = \
  $(LAB6)/alu_opcodes_pkg.sv \
  $(LAB6)/csr_pkg.sv \
  $(LAB6)/decoder_pkg.sv \
  $(LAB6)/alu.sv \
  $(LAB6)/fulladder.sv \
  $(LAB6)/interrupt_subsystem.sv \
  $(LAB6)/lsu.sv \
  $(LAB6)/decoder.sv \
  $(LAB6)/register_file.sv \
  $(LAB6)/processor_core.sv

SV_LOCAL = memory_pkg.sv instr_mem.sv data_mem.sv processor_system.sv

TB       = lab_14.tb_processor_system.sv

# ----------------------------------------------------------------------------
# Цели компиляции C → .mem
# ----------------------------------------------------------------------------
all: init_instr.mem init_data.mem disasm.S

startup.o: startup.S
	$(CC) -c $(ARCH) $< -o $@

main.o: main.c platform.h
	$(CC) -c $(CFLAGS) $< -o $@

result.elf: $(OBJ) linker_script.ld
	$(CC) $(LDFLAGS) $(OBJ) -o $@

init_instr.mem: result.elf
	$(OBJCOPY) -O verilog --verilog-data-width=4 -j .text $< $@

init_data.mem: result.elf
	$(OBJCOPY) -O verilog --verilog-data-width=4 \
	           -j .data -j .bss -j .sdata $< $@ || true
	# Удалить строку "@XXXXXXXX" (адрес LMA — в симуляции не нужна)
	@if [ -s $@ ]; then sed -i '/^@/d' $@; fi
	# Создать пустой файл если секция data отсутствует
	@touch $@

disasm.S: result.elf
	$(OBJDUMP) -D $< > $@

# ----------------------------------------------------------------------------
# Симуляция (iverilog)
# ----------------------------------------------------------------------------
sim: all
	iverilog -g2012 -o sim_lab14 \
	  $(SV_COMMON) $(SV_LOCAL) $(TB)
	vvp sim_lab14

wave: sim
	gtkwave wave.vcd

# ----------------------------------------------------------------------------
clean:
	rm -f $(OBJ) result.elf init_instr.mem init_data.mem disasm.S sim_lab14 wave.vcd

.PHONY: all sim wave clean
