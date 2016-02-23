%define name pgwrr
%define version 0.5
%define unmangled_version 0.5
%define unmangled_version 0.5
%define release 1

Summary: PowerDNS GeoIP Weighted Round Robin pipe backend plugin
Name: %{name}
Version: %{version}
Release: %{release}
License: Copyright @ 2016 Criteo
Group: Development/Libraries
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot
Prefix: %{_prefix}
BuildArch: noarch
Vendor: Robert Veznaver <r.veznaver@criteo.com>
Packager: Robert Veznaver <r.veznaver@criteo.com>
Requires: python >= 2.6 python-argparse >= 1.2.1 PyYAML >= 3.10 libyaml-devel >= 0.1.3 python-geoip2 >= 2.1.0 python-maxminddb >= 1.2.0 libmaxminddb-devel >= 1.0.4
Url: https://github.com/criteo/pgwrr
Source0: https://github.com/criteo/pgwrr/archive/v%{version}.tar.gz

%description
UNKNOWN

%prep
%setup -n %{name}-%{unmangled_version} -n %{name}-%{unmangled_version}

%build
python setup.py build

%install
python setup.py install -O1 --root=$RPM_BUILD_ROOT --record=INSTALLED_FILES

%clean
rm -rf $RPM_BUILD_ROOT

%files -f INSTALLED_FILES
%defattr(-,root,root)
