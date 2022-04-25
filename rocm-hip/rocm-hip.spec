#Cmake macro is called within sourcedir but HIP assumes it's called from build
%define __cmake_in_source_build 1
%global upstreamname hipamd

Name:           rocm-hip
Version:        5.1.0
Release:        3%{?dist}
Summary:        ROCm HIP Runtime

Url:            https://github.com/RadeonOpenCompute/hipamd
#Everything is MIT excluding the bundled khronos code is ASL 2.0:
# ROCm-OpenCL-Runtime-rocm-VERSION/khronos/headers/opencl2.2/*
# ROCm-OpenCL-Runtime-rocm-VERSION/khronos/icd/loader/icd_dispatch.h
License:        MIT and ASL 2.0
#TODO: I'd like to investigate if it's possible to reduce bundling.
# E.g. ROCclr as a subpackage of rocm-opencl or rework as a separate package
Source0:        https://github.com/ROCm-Developer-Tools/%{upstreamname}/archive/refs/tags/rocm-%{version}.tar.gz#/%{upstreamname}-%{version}.tar.gz
Source1:        https://github.com/ROCm-Developer-Tools/HIP/archive/refs/tags/rocm-%{version}.tar.gz#/HIP-%{version}.tar.gz
Source2:        https://github.com/RadeonOpenCompute/ROCm-OpenCL-Runtime/archive/refs/tags/rocm-%{version}.tar.gz#/ROCm-OpenCL-Runtime-%{version}.tar.gz
Source3:        https://github.com/ROCm-Developer-Tools/ROCclr/archive/refs/tags/rocm-%{version}.tar.gz#/ROCclr-%{version}.tar.gz

#Upstream fix:
# https://github.com/ROCm-Developer-Tools/ROCclr/commit/211c1c4d8c7f6dac48ba6c73256da60955f9dbd1
Patch0:         0001-SWDEV-323669-Fix-linux-arch-detection.patch

#Copied from rocm-opencl specfile
# fixes ppc64le ROCclr build:
Patch1:         0001-SWDEV-323669-Improve-arch-detection.patch

#A regression causes the debug symbols to not generate:
#https://github.com/ROCm-Developer-Tools/hipamd/issues/24
Patch100:       0001-Revert-hip-Fix-and-install-cmake-targets-for-hip-pac.patch
Patch101:       0002-Revert-hip-Switch-to-component-based-packaging.patch

BuildRequires:  clang-devel
BuildRequires:  cmake
BuildRequires:  git
BuildRequires:  libffi-devel
BuildRequires:  libglvnd-devel
BuildRequires:  llvm-devel
BuildRequires:  numactl-devel
BuildRequires:  ocl-icd-devel
BuildRequires:  perl
BuildRequires:  rocminfo
BuildRequires:  rocm-comgr-devel
BuildRequires:  rocminfo
BuildRequires:  rocm-runtime-devel
BuildRequires:  zlib-devel

Requires:       rocm-comgr

#Only the following architectures are supported:
# The kernel support only exists for x86_64, aarch64, and ppc64le
# 32bit userspace is excluded based on current Fedora policies
ExclusiveArch:  x86_64 aarch64 ppc64le

#rocm-hip bundles rocm-opencl and what it bundles
Provides:       bundled(rocm-opencl) = %{version}
Provides:       bundled(opencl-headers) = 2.2
Provides:       bundled(rocclr) = %{version}
#rocm-hip bundles one file from khronos' ICD loader code
# "loader/icd_dispatch.h" from:
# https://github.com/KhronosGroup/OpenCL-ICD-Loader
# The file including it is called fixme.cpp, so I assume the issue is known
Provides:       bundled(OpenCL-ICD-Loader) = 2020.03.13

%description
HIP is a C++ Runtime API and Kernel Language that allows developers to create
portable applications for AMD and NVIDIA GPUs from single source code.

%package devel
Summary:        ROCm HIP development package
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description devel
The AMD ROCm HIP development package.

%prep
%autosetup -N -b 1 -a 2 -n %{upstreamname}-rocm-%{version}

#setup macro only allows extracting up to 3 sources:
gzip -dc %{SOURCE3} | tar -xf -
pushd ROCclr-rocm-%{version}
%autopatch -p1 -m 0 -M 99
popd
%autopatch -p1 -m 100

#FIXME: some hip cmake files don't respect the Linux FHS:
sed -i "s/\(cmake DESTINATION \)./\1\${LIB_INSTALL_DIR}/" CMakeLists.txt

#HIP requires RPATH
#https://github.com/ROCm-Developer-Tools/hipamd/issues/22
sed -i "/CMAKE_INSTALL_RPATH/d" CMakeLists.txt

pushd ROCm-OpenCL-Runtime-rocm-%{version}
#Clean up unused bundled code in OpenCL
ls -d khronos/headers/* | grep -v opencl2.2 | xargs rm -r
ls -d khronos/icd/* | grep -v loader | xargs rm -r
ls -d khronos/icd/loader/* | grep -v icd_dispatch.h | xargs rm -r
#License for opencl-header 2.2 (bundled code):
cp khronos/headers/opencl2.2/LICENSE.txt ../LICENSE-OPENCL2.2.txt
popd

%build
#Set location of clang++ for hipconfig perl script run by cmake:
export HIP_CLANG_PATH=%{_bindir}
mkdir build
cd build
%cmake -S.. -B. \
    -DHIP_COMMON_DIR=$(pwd)/../../HIP-rocm-%{version} \
    -DAMD_OPENCL_PATH=$(pwd)/../ROCm-OpenCL-Runtime-rocm-%{version} \
    -DROCCLR_PATH=$(pwd)/../ROCclr-rocm-%{version} \
    -DHIP_COMPILER=clang \
    -DCMAKE_BUILD_TYPE=RelWithDebInfo
%cmake_build

%install
cd build
%cmake_install

#FIXME: cmake hardcodes libdir, instead of using cmake's gnuinstalldirs
mv %{buildroot}%{_prefix}/lib %{buildroot}%{_libdir}
sed -i "s|lib\(/libamdhip64.so\)|lib64\1|" \
    %{buildroot}%{_libdir}/cmake/hip*/*.cmake

%files
%doc README.md
%license LICENSE.txt LICENSE-OPENCL2.2.txt
%{_libdir}/.hipInfo
%{_libdir}/libamdhip64.so.5{,.*}
%{_libdir}/libhiprtc-builtins.so.5{,.*}

%files devel
%{_bindir}/*
%{_bindir}/.hipVersion
%{_includedir}/hip
%{_libdir}/libamdhip64.so
%{_libdir}/libhiprtc-builtins.so
%{_libdir}/cmake/FindHIP*
%{_libdir}/cmake/hip
%{_libdir}/cmake/hip-lang

%changelog
* Wed Apr 06 2022 Jeremy Newton <alexjnewt at hotmail dot com> - 5.1.0-3
- Copy a patch and some cleanup from rocm-opencl

* Tue Apr 05 2022 Jeremy Newton <alexjnewt at hotmail dot com> - 5.1.0-2
- Enable ppc64le

* Fri Apr 01 2022 Jeremy Newton <alexjnewt at hotmail dot com> - 5.1.0-1
- Update to 5.1.0

* Sat Mar 12 2022 Jeremy Newton <alexjnewt at hotmail dot com> - 5.0.2-1
- Initial package
