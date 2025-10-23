# CPU Profiler eBPF Probe Makefile

# Compiler settings
CLANG ?= clang
LLC ?= llc
LLVM_STRIP ?= llvm-strip
GO ?= go

# Directories
SRC_DIR := .
BUILD_DIR := build
INCLUDE_DIR := /usr/include

# Target architecture
ARCH := $(shell uname -m | sed 's/x86_64/x86/')

# eBPF program
EBPF_SRC := cpu_profiler.c
EBPF_OBJ := $(BUILD_DIR)/cpu_profiler.o

# Go userspace program
GO_SRC := cpu_profiler.go
GO_BIN := $(BUILD_DIR)/cpu_profiler

# Default target
.PHONY: all
all: $(EBPF_OBJ) $(GO_BIN)

# Create build directory
$(BUILD_DIR):
	mkdir -p $(BUILD_DIR)

# Compile eBPF program
$(EBPF_OBJ): $(EBPF_SRC) | $(BUILD_DIR)
	$(CLANG) -g -O2 -target bpf -D__TARGET_ARCH_$(ARCH) \
		-I$(INCLUDE_DIR) \
		-I/usr/include/$(shell uname -m)-linux-gnu \
		-c $(EBPF_SRC) -o $(EBPF_OBJ)
	$(LLVM_STRIP) -g $(EBPF_OBJ)

# Build Go userspace program
$(GO_BIN): $(GO_SRC) go.mod | $(BUILD_DIR)
	cd $(SRC_DIR) && CGO_ENABLED=1 $(GO) build -o $(GO_BIN) $(GO_SRC)

# Initialize Go module if needed
go.mod:
	$(GO) mod init cpu-profiler
	$(GO) mod tidy

# Install dependencies
.PHONY: deps
deps:
	$(GO) mod download
	$(GO) mod tidy

# Clean build artifacts
.PHONY: clean
clean:
	rm -rf $(BUILD_DIR)
	rm -f go.sum

# Run the profiler (requires root)
.PHONY: run
run: $(EBPF_OBJ) $(GO_BIN)
	@echo "Running CPU profiler (requires root privileges)..."
	@if [ $$(id -u) -eq 0 ]; then \
		cd $(BUILD_DIR) && ./cpu_profiler; \
	else \
		echo "Please run as root: sudo make run"; \
	fi

# Install build dependencies
.PHONY: install-deps
install-deps:
	@echo "Installing build dependencies..."
	@if command -v apt-get >/dev/null 2>&1; then \
		apt-get update && apt-get install -y \
			clang llvm libbpf-dev linux-headers-$$(uname -r) \
			golang-go build-essential; \
	elif command -v yum >/dev/null 2>&1; then \
		yum install -y clang llvm libbpf-devel kernel-headers \
			golang gcc make; \
	elif command -v pacman >/dev/null 2>&1; then \
		pacman -S clang llvm libbpf linux-headers go gcc make; \
	else \
		echo "Please install: clang, llvm, libbpf-dev, linux-headers, golang"; \
	fi

# Development helpers
.PHONY: format
format:
	$(GO) fmt ./...
	@if command -v clang-format >/dev/null 2>&1; then \
		clang-format -i $(EBPF_SRC); \
	fi

.PHONY: check
check: $(EBPF_OBJ)
	@echo "Checking eBPF program..."
	@if command -v bpftool >/dev/null 2>&1; then \
		bpftool prog show; \
	fi
	$(GO) vet ./...

# Help
.PHONY: help
help:
	@echo "CPU Profiler eBPF Probe Build System"
	@echo ""
	@echo "Targets:"
	@echo "  all          - Build both eBPF and Go programs (default)"
	@echo "  deps         - Download Go dependencies"
	@echo "  clean        - Remove build artifacts"
	@echo "  run          - Run the profiler (requires root)"
	@echo "  install-deps - Install system build dependencies"
	@echo "  format       - Format source code"
	@echo "  check        - Run basic checks"
	@echo "  help         - Show this help message"
	@echo ""
	@echo "Requirements:"
	@echo "  - Linux kernel 4.4+ with CONFIG_BPF=y"
	@echo "  - clang/llvm for eBPF compilation"
	@echo "  - Go 1.19+ for userspace program"
	@echo "  - Root privileges for running"