#!/bin/bash
set -e

FIRMWARE_DIR="${FIRMWARE_DIR:-$HOME/.config/Adv360-Pro-ZMK/firmware}"

wait_for_mount() {
  local side=$1
  echo "Waiting for $side half to mount as ADV360PRO..." >&2
  echo "  (hold Mod layer + tap bootloader key)" >&2
  while true; do
    for mount in /Volumes/ADV360PRO*; do
      if [ -d "$mount" ]; then
        echo "  mounted: $mount" >&2
        printf '%s' "$mount"
        return
      fi
    done
    sleep 1
  done
}

copy_firmware() {
  local file=$1
  local mount=$2
  echo "Copying $(basename "$file") to $mount ..."
  cp "$file" "$mount/"
  sync
  echo "  done. Ejecting..."
  diskutil eject "$mount" >/dev/null 2>&1 || true
  echo "  ejected."
}

echo "=== Flashing Kinesis Advantage 360 Pro ==="
echo ""

MOUNT=$(wait_for_mount left)
copy_firmware "$FIRMWARE_DIR/latest-left-clique.uf2" "$MOUNT"
echo ""

echo "Flashed left half. Reconnect the keyboard when ready."
