# Created by pyp2rpm-1.1.2
%global pypi_name atomicapp-builder

# if you want to package a normal release, set postrelease to 0
# if you want to package a postrelease, set it to 1 or higher to ensure proper upgrade path
%global postrelease 1
%global release 1
%global commit 940d15de1064a0497a9d4ccc8e8bcfbad03af370
%global shortcommit %(c=%{commit}; echo ${c:0:7})

Name:           %{pypi_name}
Version:        0.0.1
%if 0%{?postrelease}
Release:        %{release}.%{postrelease}.git.%{shortcommit}%{?dist}
%else
Release:        %{release}%{?dist}
%endif
Summary:        Application for building Atomicapps

License:        BSD
URL:            https://github.com/bkabrda/atomicapp-builder/
%if 0%{?postrelease}
Source0:        https://github.com/bkabrda/%{pypi_name}/archive/%{commit}/%{pypi_name}-%{commit}.tar.gz
%else
Source0:        https://pypi.python.org/packages/source/a/%{pypi_name}/%{pypi_name}-%{version}.tar.gz
%endif
BuildArch:      noarch
 
BuildRequires:  python2-devel
BuildRequires:  python-setuptools
 
Requires:       python-anymarkup
# TODO: depend on dock > 1.3.4 when it is released
Requires:       python-dock
Requires:       python-requests
Requires:       python-setuptools

%description
An application to build application images from Nulecule specification.


%prep
%if 0%{?postrelease}
%setup -q -n %{pypi_name}-%{commit}
%else
%setup -q -n %{pypi_name}-%{version}
%endif
# Remove bundled egg-info
rm -rf %{pypi_name}.egg-info

%build
%{__python2} setup.py build

%install
%{__python2} setup.py install --skip-build --root %{buildroot}

# no check section, since tests require internet access

%files
%doc README.md LICENSE
%{_bindir}/atomicapp-builder
%{python2_sitelib}/atomicapp_builder
%{python2_sitelib}/atomicapp_builder-%{version}-py?.?.egg-info

%changelog
* Mon Jun 15 2015 Slavek Kabrda <bkabrda@redhat.com> - 0.0.1-1
- Initial package.
