# Modified by: Stefan Gehrer (Robert Bosch LLC)
# Modified by: Daniel Weiße (Edgeless Systems GmbH)

# Use one of the following commands to build the manifest for Python3:
#
# - make                Building for Linux
# - make DEBUG=1        Building for Linux (with Gramine debug output)
# - make SGX=1          Building for SGX
# - make SGX=1 DEBUG=1  Building for SGX (with Gramine debug output)
#
# Use `make clean` to remove Gramine-generated files.

#include ../../Scripts/Makefile.configs

# Relative path to Gramine root
SGX_SIGNER_KEY ?= ./signing_key.pem
ARCH_LIBDIR ?= /lib/$(shell $(CC) -dumpmachine)

ifeq ($(DEBUG),1)
GRAMINE_LOG_LEVEL = debug
else
GRAMINE_LOG_LEVEL = error
endif

ifeq ($(WORKER),1)
GRAMINE_ENCLAVE_SIZE = 16G
else
GRAMINE_ENCLAVE_SIZE = 8G
endif

.PHONY: all
all: python.manifest
ifeq ($(SGX),1)
all: python.manifest.sgx python.sig python.token
endif

python.manifest: python.manifest.template
	gramine-manifest \
		-Dlog_level=$(GRAMINE_LOG_LEVEL) \
		-Darch_libdir=$(ARCH_LIBDIR) \
		-Dentrypoint=$(realpath $(shell sh -c "command -v python3")) \
		-Denclave_size=$(GRAMINE_ENCLAVE_SIZE) \
		$< >$@

# Python manifests for SGX:
#   Generating the SGX-specific manifest (python.manifest.sgx), the enclave signature,
#   and the token for enclave initialization.

python.manifest.sgx: python.manifest
	@test -s $(SGX_SIGNER_KEY) || \
	    { echo "SGX signer private key was not found, please specify SGX_SIGNER_KEY!"; exit 1; }
	gramine-sgx-sign \
		--key $(SGX_SIGNER_KEY) \
		--manifest $< \
		--output $@

python.sig: python.manifest.sgx

python.token: python.sig
	gramine-sgx-get-token --output $@ --sig $<

.PHONY: clean
clean:
	$(RM) *.manifest *.manifest.sgx *.token *.sig *.PID OUTPUT*
	$(RM) -r scripts/__pycache__

.PHONY: distclean
distclean: clean
