#!/bin/sh
# Compile touchfix (aarch64, statique, sans libc) -> recovery/root/system/bin/touchfix
set -e
cd "$(dirname "$0")"
clang --target=aarch64-linux-gnu -O2 -ffreestanding -fno-stack-protector -nostdlib -static \
      -fno-builtin -fuse-ld=lld -Wl,-e,_start -o ../../recovery/root/system/bin/touchfix touchfix.c
echo "OK : recovery/root/system/bin/touchfix"
