%global upstreamname ROCm-OpenCL-Runtime

Name:           rocm-opencl
Version:        5.1.0
Release:        3%{?dist}
Summary:        ROCm OpenCL Runtime

Url:            https://github.com/RadeonOpenCompute/ROCm-OpenCL-Runtime
#Everything is MIT excluding the bundled khronos code is ASL 2.0:
# ROCm-OpenCL-Runtime-rocm-VERSION/khronos/headers/opencl2.2/*
License:        MIT and ASL 2.0
Source0:        https://github.com/RadeonOpenCompute/%{upstreamname}/archive/refs/tags/rocm-%{version}.tar.gz#/%{upstreamname}-%{version}.tar.gz
Source1:        https://github.com/ROCm-Developer-Tools/ROCclr/archive/refs/tags/rocm-%{version}.tar.gz#/ROCclr-%{version}.tar.gz

# https://github.com/ROCm-Developer-Tools/ROCclr/commit/211c1c4d8c7f6dac48ba6c73256da60955f9dbd1
Patch0:         0001-SWDEV-323669-Fix-linux-arch-detection.patch

#I asked for upstream to give feedback on these 4 patches
# Fixes ppc64le ROCclr build:
Patch1:         0001-SWDEV-323669-Improve-arch-detection.patch
# Fixes OCL libdir install location:
Patch100:       0001-SWDEV-321118-Use-GNUInstallDirs.patch
# Allows unbundling of khronos' ocl icd loader:
Patch101:       0002-SWDEV-321116-Allow-disabling-ICD-loader.patch
Patch102:       0003-SWDEV-321116-Drop-unnecessary-ICD-include.patch

BuildRequires:  cmake
BuildRequires:  clang-devel
BuildRequires:  libglvnd-devel
BuildRequires:  numactl-devel
BuildRequires:  ocl-icd-devel
BuildRequires:  rocm-comgr-devel
BuildRequires:  rocm-runtime-devel

Requires:       rocm-comgr
Requires:       ocl-icd
Requires:       opencl-filesystem

#Only the following architectures are supported:
# The kernel support only exists for x86_64, aarch64, and ppc64le
# 32bit userspace is excluded based on current Fedora policies
ExclusiveArch:  x86_64 aarch64 ppc64le

#rocm-opencl bundles OpenCL 2.2 headers
# Some work is needed to unbundle this, as it fails to compile with latest
Provides:       bundled(opencl-headers) = 2.2
#rocm-opencl bundles rocclr
Provides:       bundled(rocclr) = %{version}

%description
ROCm OpenCL language runtime.
Supports offline and in-process/in-memory compilation.

%package devel
Summary:        ROCm OpenCL development package
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description devel
The AMD ROCm OpenCL development package.

%package -n rocm-clinfo
Summary:        ROCm OpenCL platform and device tool

%description -n rocm-clinfo
A simple ROCm OpenCL application that enumerates all possible platform and
device information.

%prep
%autosetup -N -a 1 -n %{upstreamname}-rocm-%{version}

pushd ROCclr-rocm-%{version}
%autopatch -p1 -m 0 -M 99
popd
%autopatch -p1 -m 100

#License for opencl-header 2.2 (bundled code):
cp khronos/headers/opencl2.2/LICENSE.txt LICENSE-OPENCL2.2.txt

#Clean up unused bundled code, everything except khronos/headers/opencl2.2:
ls -d khronos/* | grep -v headers | xargs rm -r
ls -d khronos/headers/* | grep -v opencl2.2 | xargs rm -r

%build
%cmake \
    -DROCM_PATH=%{_prefix} \
    -DAMD_OPENCL_PATH=$(pwd) \
    -DROCCLR_INCLUDE_DIR=ROCclr-rocm-%{version}/include \
    -DBUILD_ICD=OFF \
    -DCMAKE_BUILD_TYPE=RelWithDebInfo
%cmake_build

%install
%cmake_install

#Install ICD configuration:
install -D -m 644 config/amdocl64.icd \
    %{buildroot}%{_sysconfdir}/OpenCL/vendors/amdocl64.icd

#Avoid file conflicts with opencl-headers package:
mkdir -p %{buildroot}%{_includedir}/%{name}
mv %{buildroot}%{_includedir}/CL %{buildroot}%{_includedir}/%{name}/CL

#Avoid file conflicts with clinfo package:
mv %{buildroot}%{_bindir}/clinfo %{buildroot}%{_bindir}/rocm-clinfo

%files
%license LICENSE.txt LICENSE-OPENCL2.2.txt
%config(noreplace) %{_sysconfdir}/OpenCL/vendors/amdocl64.icd
%{_libdir}/libamdocl64.so
#TODO: cltrace does not have a proper soname:
%{_libdir}/libcltrace.so
#Duplicated files:
%exclude %{_docdir}/*/LICENSE*

%files devel
%{_includedir}/%{name}

%files -n rocm-clinfo
%license LICENSE.txt LICENSE-OPENCL2.2.txt
%{_bindir}/rocm-clinfo

%changelog
* Wed Apr 06 2022 Jeremy Newton <alexjnewt at hotmail dot com> - 5.1.0-3
- Update with proposed patches

* Tue Apr 05 2022 Jeremy Newton <alexjnewt at hotmail dot com> - 5.1.0-2
- Enable ppc64le

* Fri Apr 01 2022 Jeremy Newton <alexjnewt at hotmail dot com> - 5.1.0-1
- Update to 5.1.0
- Fix clarification of bundled code
- Delete unnecessary bundled code in prep
- Add missing rocm-comgr requires

* Sat Mar 12 2022 Jeremy Newton <alexjnewt at hotmail dot com> - 5.0.0-1
- Initial package
