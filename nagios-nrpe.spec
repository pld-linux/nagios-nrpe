Summary:	Nagios remote plugin execution service/plugin
Summary(pl.UTF-8):	Demon i wtyczka zdalnego wywoływania wtyczek Nagios
Name:		nagios-nrpe
Version:	2.13
Release:	1
License:	GPL v2
Group:		Networking
Source0:	http://downloads.sourceforge.net/nagios/nrpe-%{version}.tar.gz
# Source0-md5:	e5176d9b258123ce9cf5872e33a77c1a
Source1:	nrpe.init
Source2:	nrpe-command.cfg
Source3:	%{name}.tmpfiles
Patch0:		%{name}-config.patch
Patch1:		nrpe_check_control.patch
URL:		http://www.nagios.org/
BuildRequires:	autoconf
BuildRequires:	automake
BuildRequires:	openssl-devel
BuildRequires:	openssl-tools
BuildRequires:	rpmbuild(macros) >= 1.268
Requires(post,preun):	/sbin/chkconfig
Requires:	nagios-common
Requires:	rc-scripts
Provides:	nagios-core
Obsoletes:	netsaint-nrpe
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_sysconfdir	/etc/nagios
%define		_datadir	%{_prefix}/share/%{name}
%define		_plugindir	%{_libdir}/nagios/plugins
%define		_libexecdir	%{_plugindir}
%define		_localstatedir	%{_var}/log/nagios
%define		nsport		5666

%description
NRPE is an addon for Nagios that allows you to execute "local" plugins
(like check_disk, check_procs, etc.) on remote hosts. The check_nrpe
plugin is called from Nagios and makes plugin execution requests to
the NRPE daemon running on the remote host (either as a standalone
daemon or as a service under inetd). Supports passing command
arguments to server, as well as native SSL/TLS encryption (anonymous
DH mode).

%description -l pl.UTF-8
NRPE to dodatek do Nagiosa pozwalający na wywoływanie "lokalnych"
wtyczek (takich jak check_disk, check_procs itp.) na zdalnych
maszynach. Wtyczka check_nrpe jest wywoływana z poziomu Nagiosa i
wysyła żądania uruchomienia wtyczek do demona NRPE działającego na
zdalnej maszynie (jako samodzielny demon lub usługa inetd). Obsługuje
przekazywanie argumentów poleceń do serwera, a także natywne
szyfrowanie SSL/TLS (w trybie anonimowego DH).

%package -n nagios-plugin-check_nrpe
Summary:	check_nrpe plugin for Nagios
Summary(pl.UTF-8):	Wtyczka check_nrpe dla Nagiosa
Group:		Networking
Requires:	nagios-common
Provides:	%{name}-plugin = %{version}-%{release}
Obsoletes:	nagios-nrpe-plugin < 2.12-6

%description -n nagios-plugin-check_nrpe
check_nrpe plugin for Nagios. This plugin allows running plugins on
remote machines using nrpe service.

%description -n nagios-plugin-check_nrpe -l pl.UTF-8
Wtyczka check_nrpe dla Nagiosa. Pozwala na zdalne uruchamianie wtyczek
na innych komputerach za pomocą demona nrpe.

%prep
%setup -q -n nrpe-%{version}
%undos contrib/nrpe_check_control.c
%patch0 -p1
%patch1 -p1

%build
%{__aclocal}
%{__autoconf}
%configure \
	--with-nrpe-port=%{nsport} \
	--with-nrpe-user=nagios \
	--with-nrpe-group=nagios \
	--enable-ssl \
	--enable-command-args

%{__make} all

%{__cc} %{rpmcppflags} %{rpmcflags} %{rpmldflags} contrib/nrpe_check_control.c -o contrib/nrpe_check_control

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{/etc/rc.d/init.d,%{_sysconfdir}/{plugins,nrpe.d},%{_libdir}/nagios/plugins,%{_sbindir}} \
	$RPM_BUILD_ROOT{%{_localstatedir},/var/run/nrpe} \
	$RPM_BUILD_ROOT/usr/lib/tmpfiles.d

cp -p sample-config/nrpe.cfg $RPM_BUILD_ROOT%{_sysconfdir}/nrpe.cfg
sed -e 's,@plugindir@,%{_plugindir},' %{SOURCE2} > $RPM_BUILD_ROOT%{_sysconfdir}/plugins/check_nrpe.cfg
install -p %{SOURCE1} $RPM_BUILD_ROOT/etc/rc.d/init.d/nrpe
install -p src/nrpe $RPM_BUILD_ROOT%{_sbindir}
install -p src/check_nrpe $RPM_BUILD_ROOT%{_plugindir}

install %{SOURCE3} $RPM_BUILD_ROOT/usr/lib/tmpfiles.d/%{name}.conf

%clean
rm -rf $RPM_BUILD_ROOT

%post
/sbin/chkconfig --add nrpe
%service nrpe restart

%preun
if [ "$1" = "0" ] ; then
	%service nrpe stop
	/sbin/chkconfig --del nrpe
fi

%triggerpostun -- %{name} < 2.6-1.1
%{__sed} -i -e 's,/var/run/nrpe.pid,/var/run/nrpe/nrpe.pid,' %{_sysconfdir}/nrpe.cfg

%triggerpostun -n nagios-plugin-check_nrpe -- nagios-plugin-check_nrpe < 2.12-7.1
if [ -f %{_sysconfdir}/plugins/nrpe.cfg.rpmsave ]; then
	cp -f %{_sysconfdir}/plugins/check_nrpe.cfg{,.rpmnew}
	mv -f %{_sysconfdir}/plugins/{nrpe.cfg.rpmsave,check_nrpe.cfg}
	sed -i -e 's,-c \$ARG1\$,$ARG1$,' %{_sysconfdir}/plugins/check_nrpe.cfg
fi

%files
%defattr(644,root,root,755)
%doc Changelog LEGAL README* SECURITY
%attr(640,root,nagios) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/nrpe.cfg
%attr(750,root,nagios) %dir %{_sysconfdir}/nrpe.d
%attr(755,root,root) %{_sbindir}/nrpe
%attr(754,root,root) /etc/rc.d/init.d/nrpe
%dir %attr(775,root,nagios) /var/run/nrpe
/usr/lib/tmpfiles.d/%{name}.conf

%files -n nagios-plugin-check_nrpe
%defattr(644,root,root,755)
%attr(640,root,nagios) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/plugins/check_nrpe.cfg
%attr(755,root,root) %{_plugindir}/check_nrpe
