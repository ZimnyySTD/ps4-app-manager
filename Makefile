OO_PS4_TOOLCHAIN ?= /tmp/oo_root/usr/lib/OpenOrbisSDK
CC := clang
CFLAGS := --target=x86_64-scei-ps4-elf -fno-builtin -nostdlib -Iinclude -I$(OO_PS4_TOOLCHAIN)/include
LDFLAGS := -T $(OO_PS4_TOOLCHAIN)/link.x -L$(OO_PS4_TOOLCHAIN)/lib -lkernel -lc

OBJS := build/main.o build/app_manager.o build/ui.o

TITLE_ID := PS4APP000
CONTENT_ID := IV0000-PS4APP000_00-PS4APPMANAGER000
PKG_NAME := PS4-App-Manager.pkg

.PHONY: all clean pkg test setup

all: pkg

setup:
	python3 scripts/setup_toolchain.py

build/%.o: src/%.c
	@mkdir -p build
	$(CC) $(CFLAGS) -c $< -o $@

build/PS4AppManager.elf: $(OBJS)
	@mkdir -p build
	@mkdir -p /tmp/bin /tmp/llvm_libs
	@cp -f /tmp/oo_root/usr/lib/x86_64-linux-gnu/libLLVM-10.so.1 /tmp/llvm_libs/ 2>/dev/null || true
	@cp -f /tmp/oo_root/usr/lib/x86_64-linux-gnu/libffi.so.7* /tmp/llvm_libs/ 2>/dev/null || true
	@echo '#!/usr/bin/env bash' > /tmp/bin/orbis-ld
	@echo 'export LD_LIBRARY_PATH=/tmp/llvm_libs' >> /tmp/bin/orbis-ld
	@echo 'exec /tmp/oo_root/usr/lib/llvm-10/bin/lld -flavor gnu "$$@"' >> /tmp/bin/orbis-ld
	@chmod +x /tmp/bin/orbis-ld
	PATH=/tmp/bin:$$PATH $(CC) $(CFLAGS) $(OBJS) $(LDFLAGS) -o $@

build/eboot.bin: build/PS4AppManager.elf
	@mkdir -p build/sce_sys
	python3 $(OO_PS4_TOOLCHAIN)/scripts/make_fself.py build/PS4AppManager.elf build/eboot.bin

assets/param.sfo: scripts/generate_sfo.py
	python3 scripts/generate_sfo.py

pkg: build/eboot.bin assets/param.sfo assets/icon0.png
	python3 scripts/build_pkg.py

test:
	python3 scripts/validate_pkg.py build/$(PKG_NAME)

clean:
	rm -rf build assets/param.sfo
