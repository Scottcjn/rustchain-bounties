# Computer Space (1971) FPGA Makefile
# Builds bitstream for Lattice iCE40 UP5K

# ============================================================================
# CONFIGURATION
# ============================================================================

FPGA_CHIP = up5k
PACKAGE = sg48
PCF_FILE = fpga/computer_space.pcf
TOP_MODULE = computer_space_miner
VERILOG_FILES = fpga/computer_space_miner.v

# Output files
BITSTREAM = computer_space_miner.bit
ASCII_BITMAP = computer_space_miner.bin
LOG_FILE = build.log

# Tools
YOSYS = yosys
NEXTPNR = nextpnr-ice40
ICEPACK = icepack
ICEPROG = iceprog

# ============================================================================
# TARGETS
# ============================================================================

.PHONY: all build synth place route flash clean test simulate

all: build

# Full build flow
build: synth place route pack
	@echo "✅ Build complete!"
	@echo "   Bitstream: $(BITSTREAM)"
	@echo "   Size: $$(wc -c < $(BITSTREAM)) bytes"

# Synthesis (Yosys)
synth: $(TOP_MODULE).json
	@echo "✅ Synthesis complete"

$(TOP_MODULE).json: $(VERILOG_FILES)
	@echo "🔨 Running synthesis (Yosys)..."
	$(YOSYS) -p "synth_ice40 -top $(TOP_MODULE) -json $@" $(VERILOG_FILES) 2>&1 | tee -a $(LOG_FILE)

# Place & Route (nextpnr)
place: $(TOP_MODULE).asc
	@echo "✅ Place & Route complete"

$(TOP_MODULE).asc: $(TOP_MODULE).json $(PCF_FILE)
	@echo "🔨 Running place & route (nextpnr)..."
	$(NEXTPNR) --$(FPGA_CHIP) --package $(PACKAGE) \
		--json $(TOP_MODULE).json \
		--pcf $(PCF_FILE) \
		--asc $@ 2>&1 | tee -a $(LOG_FILE)

# Route only (if placement already done)
route: $(TOP_MODULE).asc
	@echo "✅ Route complete"

# Pack bitstream (icepack)
pack: $(BITSTREAM)
	@echo "✅ Bitstream packed"

$(BITSTREAM): $(TOP_MODULE).asc
	@echo "🔨 Packing bitstream (icepack)..."
	$(ICEPACK) $< $@ 2>&1 | tee -a $(LOG_FILE)

# Flash to FPGA (iceprog)
flash: $(BITSTREAM)
	@echo "⚡ Flashing to FPGA..."
	$(ICEPROG) $<
	@echo "✅ Flash complete!"

# Clean build artifacts
clean:
	@echo "🧹 Cleaning build artifacts..."
	rm -f $(TOP_MODULE).json $(TOP_MODULE).asc $(BITSTREAM) $(ASCII_BITMAP) $(LOG_FILE)
	rm -f *.vcd *.ghw *.vvp
	@echo "✅ Clean complete"

# Run testbench (Verilator)
test: simulate
	@echo "✅ Tests complete"

simulate: testbench.vvp
	@echo "🔬 Running simulation..."
	./testbench.vvp

testbench.vvp: fpga/computer_space_miner.v
	@echo "🔨 Compiling testbench (Verilator)..."
	verilator --cc --trace fpga/computer_space_miner.v --top-module tb_computer_space_miner
	make -C obj_dir -f Vcomputer_space_miner.mk
	# Note: Full testbench setup requires additional configuration

# Check syntax only
check:
	@echo "🔍 Checking syntax..."
	$(YOSYS) -p "read_verilog $(VERILOG_FILES); check" 2>&1 | tee -a $(LOG_FILE)
	@echo "✅ Syntax OK"

# Generate ASCII art bitmap (for terminal display)
ascii: $(BITSTREAM)
	@echo "🎨 Generating ASCII bitmap..."
	icebox_ascii.py $(BITSTREAM) > $(ASCII_BITMAP)
	@echo "✅ ASCII bitmap: $(ASCII_BITMAP)"

# Show resource utilization
resources: $(TOP_MODULE).asc
	@echo "📊 Resource utilization:"
	icebox_stat $(TOP_MODULE).asc
	@echo ""
	@echo "Logic cells: $$(grep -c 'LUT4_' $(TOP_MODULE).asc) / 5280"
	@echo "Block RAM: $$(grep -c 'RAMB_' $(TOP_MODULE).asc) / 30"
	@echo "PLL: $$(grep -c 'PLL_' $(TOP_MODULE).asc) / 1"

# Help
help:
	@echo "Computer Space (1971) FPGA Build System"
	@echo ""
	@echo "Targets:"
	@echo "  all      - Full build (default)"
	@echo "  synth    - Synthesis only (Yosys)"
	@echo "  place    - Place & Route (nextpnr)"
	@echo "  route    - Route only"
	@echo "  pack     - Pack bitstream (icepack)"
	@echo "  flash    - Flash to FPGA (iceprog)"
	@echo "  clean    - Remove build artifacts"
	@echo "  test     - Run testbench"
	@echo "  simulate - Run simulation"
	@echo "  check    - Syntax check only"
	@echo "  ascii    - Generate ASCII bitmap"
	@echo "  resources- Show resource utilization"
	@echo "  help     - Show this help"
	@echo ""
	@echo "Requirements:"
	@echo "  - yosys (synthesis)"
	@echo "  - nextpnr-ice40 (place & route)"
	@echo "  - icestorm (icepack, iceprog)"
	@echo "  - verilator (simulation)"
	@echo ""
	@echo "Install (Ubuntu/Debian):"
	@echo "  sudo apt install yosys nextpnr icestorm-tools verilator"

# Default target
.DEFAULT_GOAL := all
