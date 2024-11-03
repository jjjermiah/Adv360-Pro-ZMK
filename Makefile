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
