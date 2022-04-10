%global upstreamname ROCm-CompilerSupport

Name:           rocm-compilersupport
Version:        5.1.0
Release:        2%{?dist}
Summary:        Various AMD ROCm LLVM related services

Url:            https://github.com/RadeonOpenCompute/ROCm-CompilerSupport
License:        NCSA
Source0:        https://github.com/RadeonOpenCompute/%{upstreamname}/archive/refs/tags/rocm-%{version}.tar.gz#/%{upstreamname}-%{version}.tar.gz

#Patch to use dynamic linking for clang
# Upstream is ok with dynamic linking, but my patch isn't currently upstreamable
# since upstream wants to still allow static linking:
#https://github.com/RadeonOpenCompute/ROCm-CompilerSupport/issues/40
Patch0:         0001-Link-libclang-dynamically.patch

#https://github.com/RadeonOpenCompute/ROCm-CompilerSupport/pull/39
Patch1:         0001-Fix-cmake-file-location.patch

#Fix build against LLVM 14, cherry-picked from amd-stg-open branch:
Patch100:       0001-COMGR-changes-needed-for-https-github.com-llvm-llvm-.patch

BuildRequires:  cmake
BuildRequires:  clang-devel >= 14.0.0
BuildRequires:  lld-devel
BuildRequires:  llvm-devel >= 14.0.0
BuildRequires:  rocm-device-libs >= %(echo %{version} | sed 's/\.[0-9]*$/.0/')
BuildRequires:  zlib-devel

#Only the following architectures are useful for ROCm packages:
ExclusiveArch:  x86_64 aarch64 ppc64le

%description
This package currently contains one library, the Code Object Manager (Comgr)

%package -n rocm-comgr
Summary:        AMD ROCm LLVM Code Object Manager

%description -n rocm-comgr
The AMD Code Object Manager (Comgr) is a shared library which provides
operations for creating and inspecting code objects.

%package -n rocm-comgr-devel
Summary:        AMD ROCm LLVM Code Object Manager
Requires:       rocm-comgr%{?_isa} = %{version}-%{release}

%description -n rocm-comgr-devel
The AMD Code Object Manager (Comgr) development package.

The API is documented in the header file:
"%{_includedir}/amd_comgr.h"

%prep
%autosetup -p1 -n %{upstreamname}-rocm-%{version}

#These tests rely on features not present in upstream llvm:
sed -i -e "/compile_test/d" \
    -e "/compile_minimal_test/d" \
    -e "/compile_device_libs_test/d" \
    -e "/compile_source_with_device_libs_to_bc_test/d" \
    lib/comgr/test/CMakeLists.txt

%build
%cmake -S lib/comgr -DCMAKE_BUILD_TYPE="RELEASE" -DBUILD_TESTING=ON
%cmake_build

%check
%cmake_build --target test

%install
%cmake_install

%files -n rocm-comgr
%license LICENSE.txt lib/comgr/NOTICES.txt
%doc lib/comgr/README.md
%{_libdir}/libamd_comgr.so.2{,.*}
#Files already included:
%exclude %{_docdir}/amd_comgr/comgr/LICENSE.txt
%exclude %{_datadir}/amd_comgr/LICENSE.txt
%exclude %{_datadir}/amd_comgr/NOTICES.txt
%exclude %{_datadir}/amd_comgr/README.md

%files -n rocm-comgr-devel
%{_includedir}/amd_comgr.h
%{_libdir}/libamd_comgr.so
%{_libdir}/cmake/amd_comgr

%changelog
* Tue Apr 05 2022 Jeremy Newton <alexjnewt at hotmail dot com> - 5.1.0-2
- Enable ppc64le

* Tue Mar 29 2022 Jeremy Newton <alexjnewt at hotmail dot com> - 5.1.0-1
- Update to 5.1.0

* Fri Feb 11 2022 Jeremy Newton <alexjnewt at hotmail dot com> - 5.0.0-1
- Update to 5.0.0

* Mon Jan 24 2022 Jeremy Newton <alexjnewt at hotmail dot com> - 4.5.2-1
- Initial package
