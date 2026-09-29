#!/bin/bash
set -e
DEVICE=ac8257_demo
VENDOR=alps
MY_DIR="${BASH_SOURCE%/*}"; [ -d "$MY_DIR" ] || MY_DIR="$PWD"
ANDROID_ROOT="${MY_DIR}/../../.."
source "${ANDROID_ROOT}/tools/extract-utils/extract_utils.sh"
setup_vendor "$DEVICE" "$VENDOR" "$ANDROID_ROOT"
write_headers
write_makefiles "${MY_DIR}/proprietary-files.txt" true
write_footers
