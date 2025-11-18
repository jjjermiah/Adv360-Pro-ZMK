#!/usr/bin/env bash
set -e

PIXI_PATH=$HOME/.pixi/bin/pixi

# Determine which container runtime to use
DOCKER=$(command -v podman || command -v docker)
if [ -z "$DOCKER" ]; then
    echo "Error: Neither podman nor docker found in PATH"
    exit 1
fi

# Get timestamp and commit
TIMESTAMP=$(date -u +"%Y%m%d%H%M")
COMMIT=$(git rev-parse --short HEAD 2>/dev/null || echo "unknown")

# Detect OS for SELinux settings
if [[ "$(uname)" == "Darwin" ]]; then
    SELINUX1=""
    SELINUX2=""
else
    SELINUX1=":z"
    SELINUX2=",z"
fi

# Get version info
bin/get_version_local.sh clique >> /dev/null

# Build Docker image
echo "Building Docker image..."
$DOCKER build --tag zmk --file Dockerfile .

# Run build for both left and right
echo "Building firmware..."
$DOCKER run --rm -it --name zmk \
    -v "$(pwd)/firmware:/app/firmware${SELINUX1}" \
    -v "$(pwd)/config:/app/config:ro${SELINUX2}" \
    -e TIMESTAMP="$TIMESTAMP" \
    -e COMMIT="$COMMIT" \
    -e BUILD_RIGHT=true \
    zmk

# Reset version.dtsi
git checkout config/version.dtsi
echo "Build complete! Firmware files are in firmware/"
echo ""
echo "Waiting for ADV360 board to be mounted..."
echo "(Press Ctrl+C to cancel)"

# Watch for ADV360 board mount
while true; do
    # Check for ADV360PRO mount (macOS checks /Volumes)
    if [ -d "/Volumes/ADV360PRO" ]; then
        echo ""
        echo "✓ ADV360PRO found at: /Volumes/ADV360PRO"
        echo ""
        echo "Copyinng firmware..."
        # run cp firmware/latest-left-clique.uf2 /Volumes/ADV360PRO  
        # if it passes exit gracefully
        cp firmware/latest-left-clique.uf2 /Volumes/ADV360PRO;
        echo "✓ Firmware copied successfully!"
        echo ""
        echo "Generating SVG keymap..."
        if $PIXI_PATH run svg; then
            echo "✓ SVG generated successfully!"
            echo ""
            echo "Committing changes..."
            git add -A
            git commit -m "Update firmware and keymap visualization - $(date +%Y%m%d%H%M)"
            echo "✓ Changes committed!"
        else
            echo "✗ Failed to generate SVG or commit."
            exit 1
        fi

        exit 0
    fi
    echo "Waiting for mount, press bootloader key..."
    sleep 2
done
