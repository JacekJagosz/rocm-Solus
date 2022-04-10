Name:           rocm-cmake
Version:        5.1.0
Release:        1%{?dist}
Summary:        ROCm HIP Runtime

Url:            https://github.com/RadeonOpenCompute/rocm-cmake
License:        MIT
Source0:        https://github.com/RadeonOpenCompute/%{name}/archive/refs/tags/rocm-%{version}.tar.gz#/%{name}-%{version}.tar.gz

#FIXME: This is a noarch package, cmake shouldn't request gcc 
BuildRequires:  gcc
BuildRequires:  gcc-c++
BuildRequires:  cmake

BuildArch:      noarch

%description
ROCM cmake modules provides cmake modules for common build tasks needed for the
ROCM software stack.

%prep
%autosetup -p1 -n %{name}-rocm-%{version}

#Remove exec perm from changelog
chmod a-x CHANGELOG.md

%build
%cmake
%cmake_build

%install
%cmake_install

# We install this via license macro instead:
rm %{buildroot}%{_docdir}/%{name}/LICENSE

%files
%doc CHANGELOG.md
%license LICENSE
%{_datadir}/rocm

%changelog
* Fri Apr 01 2022 Jeremy Newton <alexjnewt at hotmail dot com> - 5.1.0-1
- Update to 5.1.0

* Thu Feb 24 2022 Jeremy Newton <alexjnewt at hotmail dot com> - 5.0.0-1
- Initial package
