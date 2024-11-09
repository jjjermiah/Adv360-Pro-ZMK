# This Makefile is used to build and manage the firmware for a custom keyboard using Docker or Podman.
# It includes targets to build the firmware for both the left and right parts of the keyboard, as well as
# targets to clean up the generated firmware files and Docker images.
#
# Key Variables:
# - DOCKER: Determines whether to use Podman or Docker for container operations.
# - TIMESTAMP: Captures the current timestamp in UTC for versioning.
# - COMMIT: Gets the current short git commit hash.
# - SELINUX1, SELINUX2: Handles SELinux file context differences between macOS and other systems.
#
# Key Targets:
# - all: Builds and runs the firmware for the right part of the keyboard.
# - left: Builds and runs the firmware for the left part of the keyboard.
# - clean_firmware: Removes all firmware files.
# - clean_image: Removes Docker images used for building.
# - clean: Cleans both firmware files and Docker images.
#
# Usage:
# - To build and run the firmware for the right part of the keyboard, run `make all`.
# - To build and run the firmware for the left part of the keyboard, run `make left`.
# - To clean up firmware files, run `make clean_firmware`.
# - To clean up Docker images, run `make clean_image`.
# - To clean up both firmware files and Docker images, run `make clean`.

# Determine whether to use podman or docker for container operations
DOCKER := $(shell { command -v podman || command -v docker; })

# Capture the current timestamp in UTC for versioning
TIMESTAMP := $(shell date -u +"%Y%m%d%H%M")

# Get the current short git commit hash
COMMIT := $(shell git rev-parse --short HEAD 2>/dev/null)

# Conditional logic to handle SELinux file context differences between macOS and other systems
ifeq ($(shell uname),Darwin)
# On macOS, no SELinux context is required
SELINUX1 :=
SELINUX2 :=
else
# On non-macOS systems, SELinux context is added
SELINUX1 := :z
SELINUX2 := ,z
endif

# Define phony targets that do not correspond to actual files
.PHONY: all left clean_firmware clean_image clean

# Target to build and run the firmware for the right part of the keyboard
all:
	# Update version information
	$(shell bin/get_version.sh >> /dev/null)

	# Build the Docker image with the tag 'zmk'
	$(DOCKER) build --tag zmk --file Dockerfile .

	# Run the Docker image with environment variables set
	$(DOCKER) run --rm -it --name zmk \
		-v $(PWD)/firmware:/app/firmware$(SELINUX1) \
		-v $(PWD)/config:/app/config:ro$(SELINUX2) \
		-e TIMESTAMP=$(TIMESTAMP) \
		-e COMMIT=$(COMMIT) \
		-e BUILD_RIGHT=true \
		zmk

	# Revert changes made to the version configuration file
	git checkout config/version.dtsi

# Target to build and run the firmware for the left part of the keyboard
left:
	# Update version information
	$(shell bin/get_version.sh >> /dev/null)

	# Build the Docker image with the tag 'zmk'
	$(DOCKER) build --tag zmk --file Dockerfile .

	# Run the Docker image with environment variables set
	$(DOCKER) run --rm -it --name zmk \
		-v $(PWD)/firmware:/app/firmware$(SELINUX1) \
		-v $(PWD)/config:/app/config:ro$(SELINUX2) \
		-e TIMESTAMP=$(TIMESTAMP) \
		-e COMMIT=$(COMMIT) \
		-e BUILD_RIGHT=false \
		zmk

	# Revert changes made to the version configuration file
	git checkout config/version.dtsi

# Target to remove all firmware files
clean_firmware:
	rm -f firmware/*.uf2

# Target to remove Docker images used for building
clean_image:
	$(DOCKER) image rm zmk docker.io/zmkfirmware/zmk-build-arm:stable

# Target to clean both firmware and images
clean: clean_firmware clean_image
