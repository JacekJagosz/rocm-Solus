#Image support is x86 only
%ifarch x86_64
%global enableimage 1
%endif

Name:       rocm-runtime
Version:    5.1.1
Release:    1%{?dist}
Summary:    ROCm Runtime Library

License:    NCSA
URL:        https://github.com/RadeonOpenCompute/ROCR-Runtime
Source0:    https://github.com/RadeonOpenCompute/ROCR-Runtime/archive/refs/tags/rocm-%{version}.tar.gz#/%{name}-%{version}.tar.gz

#https://github.com/RadeonOpenCompute/ROCR-Runtime/pull/129
Patch0:     0001-Use-CMAKE_INSTALL_LIBDIR.patch
Patch1:     0002-fix-link-time-ordering-condition.patch

ExclusiveArch:  x86_64 aarch64 ppc64le

BuildRequires:  clang
BuildRequires:  cmake
BuildRequires:  elfutils-libelf-devel
BuildRequires:  hsakmt-devel
%if 0%{?enableimage}
BuildRequires:  clang-devel
BuildRequires:  lld-devel
BuildRequires:  llvm-devel
BuildRequires:  rocm-device-libs
BuildRequires:  vim-common
%endif

%description
The ROCm Runtime Library is a thin, user-mode API that exposes the necessary
interfaces to access and interact with graphics hardware driven by the AMDGPU
driver set and the AMDKFD kernel driver. Together they enable programmers to
directly harness the power of AMD discrete graphics devices by allowing host
applications to launch compute kernels directly to the graphics hardware.

%package devel
Summary: ROCm Runtime development files
Requires: %{name}%{?_isa} = %{version}-%{release}
Requires: hsakmt(rocm) = %{version}

%description devel
ROCm Runtime development files


%prep
%autosetup -n ROCR-Runtime-rocm-%{version} -p1

%build
%cmake -S src -DCMAKE_BUILD_TYPE=RelWithDebInfo \
    %{?!enableimage:-DIMAGE_SUPPORT=OFF} \
    -DBITCODE_DIR="%{_libdir}/amdgcn/bitcode"
%cmake_build


%install
%cmake_install

# We install this via license macro instead:
rm %{buildroot}%{_docdir}/hsa-runtime64/LICENSE.md

rm -rf %{buildroot}/usr/hsa

%ldconfig_scriptlets

%files
%doc README.md
%license LICENSE.txt
%{_libdir}/libhsa-runtime64.so.1
%{_libdir}/libhsa-runtime64.so.1.5.0

%files devel
%{_includedir}/hsa/
%{_libdir}/libhsa-runtime64.so
%{_libdir}/cmake/hsa-runtime64/

%changelog
* Sat Apr 09 2022 Jeremy Newton <alexjnewt at hotmail dot com> - 5.1.1-1
- Update to ROCm version 5.1.1

* Tue Apr 05 2022 Jeremy Newton <alexjnewt at hotmail dot com> - 5.1.0-2
- Enable ppc64le

* Thu Mar 31 2022 Jeremy Newton <alexjnewt at hotmail dot com> - 5.1.0-1
- Update to ROCm version 5.1.0

* Tue Feb 15 2022 Jeremy Newton <alexjnewt at hotmail dot com> - 5.0.0-2
- Enable image support for x86

* Fri Feb 11 2022 Jeremy Newton <alexjnewt at hotmail dot com> - 5.0.0-1
- Update to ROCm version 5.0.0
- General improvements to spec file

* Fri Jan 21 2022 Fedora Release Engineering <releng@fedoraproject.org> - 3.9.0-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_36_Mass_Rebuild

* Fri Jul 23 2021 Fedora Release Engineering <releng@fedoraproject.org> - 3.9.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_35_Mass_Rebuild

* Wed Jan 27 2021 Fedora Release Engineering <releng@fedoraproject.org> - 3.9.0-1
- Rebuilt for https://fedoraproject.org/wiki/Fedora_34_Mass_Rebuild

* Thu Nov 26 2020 Philipp Knechtges <philipp-dev@knechtges.com> - 3.9.0-0
- Version 3.9.0

* Sat Aug 01 2020 Fedora Release Engineering <releng@fedoraproject.org> - 3.5.0-3
- Second attempt - Rebuilt for
  https://fedoraproject.org/wiki/Fedora_33_Mass_Rebuild

* Wed Jul 29 2020 Fedora Release Engineering <releng@fedoraproject.org> - 3.5.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_33_Mass_Rebuild

* Wed Jul 15 2020 Tom Stellard <tstellar@redhat.com> - 3.5.0-1
- ROCm 3.5.0 Release

* Thu Jan 30 2020 Fedora Release Engineering <releng@fedoraproject.org> - 2.0.0-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_32_Mass_Rebuild

* Fri Jul 26 2019 Fedora Release Engineering <releng@fedoraproject.org> - 2.0.0-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_31_Mass_Rebuild

* Thu Mar 21 2019 Tom Stellard <tstellar@redhat.com> - 2.0.0-3
- Add endian detection for AArch64

* Sat Feb 02 2019 Fedora Release Engineering <releng@fedoraproject.org> - 2.0.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_30_Mass_Rebuild

* Mon Jan 14 2019 Tom Stellard <tstellar@redhat.com> - 2.0.0-1
- ROCm 2.0.0 Release

* Sat Jul 14 2018 Fedora Release Engineering <releng@fedoraproject.org> - 1.6.1-8
- Rebuilt for https://fedoraproject.org/wiki/Fedora_29_Mass_Rebuild

* Tue Feb 13 2018 Tom Stellard <tstellar@redhat.com> - 1.6.1-7
- Build for aarch64

* Wed Feb 07 2018 Tom Stellard <tstellar@redhat.com> - 1.6.1-6
- Add ExclusiveArch: x86_64

* Tue Feb 06 2018 Tom Stellard <tstellar@redhat.com> - 1.6.1-5
- Take ownership of /usr/include/hsa

* Fri Feb 02 2018 Tom Stellard <tstellar@redhat.com> - 1.6.1-4
- Fix build with gcc 8

* Thu Feb 01 2018 Tom Stellard <tstellar@redhat.com> - 1.6.1-3
- Use version macro in source url

* Mon Jan 29 2018 Tom Stellard <tstellar@redhat.com> - 1.6.1-2
- Fix some rpmlint errors

* Thu Oct 12 2017 Tom Stellard <tstellar@redhat.com> - 1.6.1-1
- Initial Release
