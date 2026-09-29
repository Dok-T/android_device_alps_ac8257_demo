#!/bin/bash
# Squelette LineageOS extract-utils : ./extract-files.sh <dossier_du_dump_monte>
set -e
DEVICE=ac8257_demo
VENDOR=alps
MY_DIR="${BASH_SOURCE%/*}"; [ -d "$MY_DIR" ] || MY_DIR="$PWD"
ANDROID_ROOT="${MY_DIR}/../../.."
HELPER="${ANDROID_ROOT}/tools/extract-utils/extract_utils.sh"
[ -f "$HELPER" ] || { echo "extract_utils.sh introuvable"; exit 1; }
source "$HELPER"
setup_vendor "$DEVICE" "$VENDOR" "$ANDROID_ROOT" false "${CLEAN_VENDOR:-true}"
extract "${MY_DIR}/proprietary-files.txt" "${1:-adb}" "${KANG}" --section "${SECTION}"
"${MY_DIR}/setup-makefiles.sh"
