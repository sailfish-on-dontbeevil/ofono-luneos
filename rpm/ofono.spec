Name:       ofono
Summary:    Open Source Telephony
Version:    2.19
Release:    1
License:    GPLv2
URL:        https://github.com/sailfishos/ofono
Source:     %{name}-%{version}.tar.bz2

Patch0:     0001-common-create-GList-helper-ofono_call_compare.patch
#Patch1:     0002-Add-support-for-the-Ericsson-F5521gw-modem.patch
Patch2:     0002-common-atmodem-move-at_util_call_compare_by_status-t.patch
Patch3:     0003-common-atmodem-move-at_util_call_compare_by_id-to-dr.patch
Patch4:     0004-add-call-list-helper-to-manage-voice-call-lists.patch
Patch5:     0006-Allow-qmi-qrtr-without-data.patch
Patch6:     0007-sim-add-org.ofono.EuiccManager-interface.patch
Patch7:     0008-qmimodem-add-logical-channel-support.patch
Patch8:     0100-build-export-daemon-internals-to-external-plugins.patch
Patch9:     0101-core-add-a-runtime-atom-driver-registry.patch
Patch10:    0102-core-restore-the-public-atom-driver-registration-API.patch
Patch11:    0103-core-make-the-shared-3GPP-enumerations-public.patch
Patch12:    0104-core-expose-the-atom-accessors-external-drivers-need.patch
Patch13:    0105-core-answer-the-legacy-provisioning-API-from-the-pro.patch
Patch14:    0106-core-add-the-public-helper-facade-from-ofono-misc.h.patch
Patch16:    0107-core-let-plugins-use-oFono-s-storage-directory.patch
Patch17:    0108-core-add-SIM-iccid-imsi-watches-and-the-netreg-opera.patch
Patch18:    0109-core-let-callers-build-a-PropertyChanged-signal-with.patch
Patch19:    0110-core-add-open_channel2-and-the-STK-ready-callback.patch
Patch20:    0111-core-restore-Sailfish-s-exact-SIM-driver-version-bou.patch
Patch21:    0112-core-make-the-public-headers-self-contained.patch
Patch22:    0113-build-make-the-installed-headers-usable-from-out-of-.patch
Patch23:    0114-radio-settings-never-report-a-technology-preference-.patch
Patch24:    0115-ussd-accept-pre-decoded-UTF-8-from-drivers.patch

%define libglibutil_version 1.0.51

# license macro requires rpm >= 4.11
# Recommends requires rpm >= 4.12
BuildRequires: pkgconfig(rpm)
%define license_support %(pkg-config --exists 'rpm >= 4.11'; echo $?)
%define can_recommend %(pkg-config --exists 'rpm >= 4.12'; echo $?)
%if %{can_recommend} == 0
%define recommend Recommends
%else
%define recommend Requires
%endif

Requires:   dbus
Requires:   systemd
Requires:   ell
%{recommend}: mobile-broadband-provider-info
%{recommend}: ofono-configs
Requires(preun): systemd
Requires(post): systemd
Requires(postun): systemd

BuildRequires:  pkgconfig
BuildRequires:  pkgconfig(dbus-1)
BuildRequires:  pkgconfig(libudev) >= 145
BuildRequires:  pkgconfig(libwspcodec) >= 2.0
BuildRequires:  pkgconfig(libglibutil) >= %{libglibutil_version}
BuildRequires:  pkgconfig(libdbuslogserver-dbus)
BuildRequires:  pkgconfig(libdbusaccess)
BuildRequires:  pkgconfig(mobile-broadband-provider-info)
BuildRequires:  pkgconfig(systemd)
BuildRequires:  libtool
BuildRequires:  automake
BuildRequires:  autoconf
BuildRequires:  ell-devel >= 0.68

%description
Telephony stack

%package devel
Summary:    Headers for oFono
Requires:   %{name} = %{version}-%{release}

%description devel
Development headers and libraries for oFono

%package tests
Summary:    Test Scripts for oFono
Requires:   %{name} = %{version}-%{release}
Requires:   dbus-python3
Requires:   python3-gobject
Provides:   ofono-test >= 1.0
Obsoletes:  ofono-test < 1.0

%description tests
Scripts for testing oFono and its functionality

%package doc
Summary:   Documentation for %{name}
Requires:  %{name} = %{version}-%{release}

%description doc
Man pages for %{name}.

%prep
%autosetup -p1 -n %{name}-%{version}/upstream

./bootstrap

%build
autoreconf --force --install

%configure --disable-static \
    --enable-test \
    --enable-sailfish-slot \
    --enable-sailfish-bt \
    --enable-sailfish-pushforwarder \
    --enable-sailfish-access \
    --disable-rilmodem \
    --disable-isimodem \
    --enable-qmimodem \
    --with-systemdunitdir=%{_unitdir} \
    --enable-external-ell \
    --enable-debug=yes

make %{_smp_mflags}

%check
# run unit tests
make check

%install
export DONT_STRIP=1
rm -rf %{buildroot}
%make_install

mkdir -p %{buildroot}/%{_sysconfdir}/ofono/push_forwarder.d
mkdir -p %{buildroot}%{_unitdir}/network.target.wants
mkdir -p %{buildroot}/var/lib/ofono
ln -s ../ofono.service %{buildroot}%{_unitdir}/network.target.wants/ofono.service

mkdir -p %{buildroot}%{_docdir}/%{name}-%{version}
install -m0644 -t %{buildroot}%{_docdir}/%{name}-%{version} \
        ChangeLog AUTHORS README

%preun
if [ "$1" -eq 0 ]; then
systemctl stop ofono.service ||:
fi

%post
systemctl daemon-reload ||:
# Do not restart during update
# We don't want to break anything during update
# New daemon is taken in use after reboot
# systemctl reload-or-try-restart ofono.service ||:

%postun
systemctl daemon-reload ||:

%transfiletriggerin -- %{_libdir}/ofono/plugins
systemctl try-restart ofono.service ||:

%files
%defattr(-,root,root,-)
%config %{_sysconfdir}/dbus-1/system.d/*.conf
%{_sbindir}/*
%{_unitdir}/network.target.wants/ofono.service
%{_unitdir}/ofono.service
%dir %{_sysconfdir}/ofono/
%dir %{_sysconfdir}/ofono/push_forwarder.d
# This file is part of phonesim and not needed with ofono.
%exclude %{_sysconfdir}/ofono/phonesim.conf
%dir %attr(775,radio,radio) /var/lib/ofono
%if %{license_support} == 0
%license COPYING
%endif
%{_datadir}/ofono/provision.db

%files devel
%defattr(-,root,root,-)
%{_includedir}/ofono/
%{_libdir}/pkgconfig/ofono.pc

%files tests
%defattr(-,root,root,-)
%{_libdir}/%{name}/test/*

%files doc
%defattr(-,root,root,-)
%{_mandir}/man8/%{name}d.*
%{_docdir}/%{name}-%{version}
