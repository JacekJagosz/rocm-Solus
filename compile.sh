#!/bin/bash

set -eox pipefail

order="hsakmt python-cppheaderparser rocm-cmake rocm-device-libs rocm-compilersupport rocm-runtime rocm-smi rocm-info rocm-opencl rocm-hip" #"rocblas miopen rocfft hipfft rocprim hipcub rocprofiler roctracer rocsparse hipsparse rocsolver hipsolver hipblas rocthrust rocrand rccl hipmagma"

# Check if directory exists
for pkg in $order; do
	file $pkg/package.yml
done

# Build
for pkg in $order; do
	pushd $pkg
	solbuild build
	cp *.eopkg ../build
	chown -R jacek ../build
	pushd
done
