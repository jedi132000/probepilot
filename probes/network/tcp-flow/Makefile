# TCP Flow Monitor Probe Makefile

CLANG ?= clang
LLC ?= llc
STRIP ?= llvm-strip
GO ?= go

# Target architecture
ARCH := $(shell uname -m | sed 's/x86_64/amd64/' | sed 's/aarch64/arm64/')

# Kernel headers and BPF includes
KERNEL_RELEASE := $(shell uname -r)
KERNEL_HEADERS := /usr/src/linux-headers-$(KERNEL_RELEASE)
LIBBPF_HEADERS := /usr/include

# Compiler flags
CFLAGS := -O2 -g -Wall -Werror
CFLAGS += -target bpf
CFLAGS += -D__TARGET_ARCH_$(ARCH)
CFLAGS += -I$(LIBBPF_HEADERS)
CFLAGS += -I$(KERNEL_HEADERS)/include
CFLAGS += -I$(KERNEL_HEADERS)/arch/x86/include
CFLAGS += -I$(KERNEL_HEADERS)/arch/x86/include/generated
CFLAGS += -I$(KERNEL_HEADERS)/include/generated

# Go build flags
GOFLAGS := -ldflags "-s -w"

# Targets
BPF_OBJ := tcp_flow.o
GO_BINARY := tcp_flow_monitor

.PHONY: all clean build install test deps

all: build

# Generate vmlinux.h if not exists
vmlinux.h:
	@echo "Generating vmlinux.h..."
	@if command -v bpftool >/dev/null 2>&1; then \
		bpftool btf dump file /sys/kernel/btf/vmlinux format c > vmlinux.h; \
	else \
		echo "Warning: bpftool not found, using pre-generated vmlinux.h"; \
		wget -q https://raw.githubusercontent.com/libbpf/libbpf-bootstrap/master/vmlinux/vmlinux.h; \
	fi

# Build eBPF object file
$(BPF_OBJ): tcp_flow.c vmlinux.h
	@echo "Building eBPF program..."
	$(CLANG) $(CFLAGS) -c tcp_flow.c -o $(BPF_OBJ)
	$(STRIP) -g $(BPF_OBJ)

# Build Go userspace program
$(GO_BINARY): tcp_flow.go $(BPF_OBJ)
	@echo "Building Go userspace program..."
	$(GO) mod tidy
	$(GO) build $(GOFLAGS) -o $(GO_BINARY) tcp_flow.go

# Build everything
build: $(BPF_OBJ) $(GO_BINARY)

# Install dependencies
deps:
	@echo "Installing dependencies..."
	@echo "Checking for required tools..."
	@command -v $(CLANG) >/dev/null 2>&1 || { echo "Error: clang not found"; exit 1; }
	@command -v $(GO) >/dev/null 2>&1 || { echo "Error: go not found"; exit 1; }
	@echo "Installing Go dependencies..."
	$(GO) mod download

# Test the probe (requires root)
test: build
	@echo "Testing TCP flow monitor..."
	@if [ "$$(id -u)" -ne 0 ]; then \
		echo "Error: Tests require root privileges"; \
		echo "Run: sudo make test"; \
		exit 1; \
	fi
	@echo "Starting TCP flow monitor for 10 seconds..."
	timeout 10 ./$(GO_BINARY) || true

# Install to system (requires root)
install: build
	@if [ "$$(id -u)" -ne 0 ]; then \
		echo "Error: Installation requires root privileges"; \
		echo "Run: sudo make install"; \
		exit 1; \
	fi
	@echo "Installing TCP flow monitor..."
	install -d /usr/local/bin/probepilot/
	install -m 755 $(GO_BINARY) /usr/local/bin/probepilot/
	install -m 644 $(BPF_OBJ) /usr/local/bin/probepilot/
	@echo "Installed to /usr/local/bin/probepilot/"

# Verify eBPF program
verify: $(BPF_OBJ)
	@echo "Verifying eBPF program..."
	@if command -v bpftool >/dev/null 2>&1; then \
		bpftool prog load $(BPF_OBJ) /sys/fs/bpf/tcp_flow_test 2>/dev/null && \
		bpftool prog del pinned /sys/fs/bpf/tcp_flow_test && \
		echo "✓ eBPF program verification passed"; \
	else \
		echo "Warning: bpftool not available for verification"; \
	fi

# Clean build artifacts
clean:
	@echo "Cleaning build artifacts..."
	rm -f $(BPF_OBJ) $(GO_BINARY)
	rm -f vmlinux.h
	$(GO) clean

# Show system information
sysinfo:
	@echo "=== System Information ==="
	@echo "Kernel version: $(KERNEL_RELEASE)"
	@echo "Architecture: $(ARCH)"
	@echo "Kernel headers: $(KERNEL_HEADERS)"
	@echo "Clang version: $$($(CLANG) --version | head -n1)"
	@echo "Go version: $$($(GO) version)"
	@echo "=========================="

# Development helpers
dev-setup:
	@echo "Setting up development environment..."
	$(GO) mod init tcp-flow-monitor 2>/dev/null || true
	$(GO) get github.com/cilium/ebpf@latest
	@echo "Development environment ready"

help:
	@echo "TCP Flow Monitor Probe - Available targets:"
	@echo "  all       - Build everything (default)"
	@echo "  build     - Build eBPF and Go programs"
	@echo "  deps      - Install dependencies"
	@echo "  test      - Test the probe (requires root)"
	@echo "  install   - Install to system (requires root)"
	@echo "  verify    - Verify eBPF program"
	@echo "  clean     - Clean build artifacts"
	@echo "  sysinfo   - Show system information"
	@echo "  dev-setup - Set up development environment"
	@echo "  help      - Show this help"