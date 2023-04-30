#!/bin/bash

set -eox pipefail

order="hsakmt rocm-device-libs rocm-runtime rocm-smi rocm-info rocm-cmake rocm-compiler-support rocm-opencl rocm-hip" #"rocblas miopen rocfft hipfft rocprim hipcub rocprofiler roctracer rocsparse hipsparse rocsolver hipsolver hipblas rocthrust rocrand rccl hipmagma"

# Check if directory exists
for pkg in $order; do
	file $pkg/package.yml
done

# Build
for pkg in $order; do
	pushd $pkg
	solbuild build -p rocm
	cp *.eopkg ../build
	chown -R jacek ../build
	pushd
done
