#!/bin/sh
#
# This works around bug where, by default, macOS 14.x writes part of a file
# immediately, and then doesn't update the directory for 20-60 seconds, causing
# the file system to be corrupted.
#

# Find the disk associated with ADV360PRO by running `df` and using `grep` and `cut` to extract the device identifier
disky=$(df | grep ADV360PRO | cut -d" " -f1)

# Check if disky is empty; if so, print an error message and exit with failure
if [ -z "$disky" ]; then
  echo "Error: ADV360PRO disk not found."
  exit 1
fi 

printf "ADV360PRO disk found at %s\n" "$disky"

# Ensure the ./Volumes directory exists
mkdir -p ./Volumes

# Attempt to unmount the ADV360PRO volume if it's mounted
if mount | grep -q "./Volumes/ADV360PRO"; then
  umount ./Volumes/ADV360PRO
fi


# Create the ADV360PRO directory under ./Volumes
mkdir -p ./Volumes/ADV360PRO
# Create the ADV360PRO directory under ./Volumes
mkdir -p ./Volumes/ADV360PRO

# Pause execution for 2 seconds to ensure previous commands complete
sleep 2

# # Mount the disk at ./Volumes/ADV360PRO with noasync option to prevent delayed writes
# mount -v -o noasync -t msdos $disky ./Volumes/ADV360PRO

# use diskutil to mount the disk at ./Volumes/ADV360PRO with noasync option to prevent delayed writes
sudo mount -t msdos /dev/disk4 /Volumes/ADV
