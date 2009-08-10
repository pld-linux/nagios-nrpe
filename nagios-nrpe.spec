Summary:	Nagios remote plugin execution service/plugin
Summary(pl.UTF-8):	Demon i wtyczka zdalnego wywoływania wtyczek Nagios
Name:		nagios-nrpe
Version:	2.12
Release:	5
License:	GPL v2
Group:		Networking
Source0:	http://dl.sourceforge.net/nagios/nrpe-%{version}.tar.gz
# Source0-md5:	b2d75e2962f1e3151ef58794d60c9e97
Source1:	nrpe.init
Source2:	nrpe-command.cfg
Patch0:		%{name}-config.patch
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

%package plugin
Summary:	check_nrpe plugin for Nagios
Summary(pl.UTF-8):	Wtyczka check_nrpe dla Nagiosa
Group:		Networking
Requires:	nagios-core

%description plugin
check_nrpe plugin for Nagios. This plugin allows running plugins on
remote machines using nrpe service.

%description plugin -l pl.UTF-8
Wtyczka check_nrpe dla Nagiosa. Pozwala na zdalne uruchamianie wtyczek
na innych komputerach za pomocą demona nrpe.

%prep
%setup -q -n nrpe-%{version}
%patch0 -p1

%build
%{__aclocal}
%{__autoconf}

%configure \
	--with-init-dir=/etc/rc.d/init.d \
	--with-nrpe-port=%{nsport} \
	--with-nrpe-user=nagios \
	--with-nrpe-grp=nagios \
	--enable-ssl \
	--enable-command-args

%{__make} all

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{/etc/rc.d/init.d,%{_sysconfdir}/plugins,%{_libdir}/nagios/plugins,%{_sbindir}} \
	$RPM_BUILD_ROOT{%{_localstatedir},/var/run/nrpe}

install sample-config/nrpe.cfg $RPM_BUILD_ROOT%{_sysconfdir}/nrpe.cfg
sed -e 's,@plugindir@,%{_plugindir},' %{SOURCE2} > $RPM_BUILD_ROOT%{_sysconfdir}/plugins/nrpe.cfg
install %{SOURCE1} $RPM_BUILD_ROOT/etc/rc.d/init.d/nrpe
install src/nrpe $RPM_BUILD_ROOT%{_sbindir}
install src/check_nrpe $RPM_BUILD_ROOT%{_plugindir}

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

%files
%defattr(644,root,root,755)
%doc Changelog LEGAL README* SECURITY
%attr(640,root,nagios) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/nrpe.cfg
%attr(755,root,root) %{_sbindir}/nrpe
%attr(754,root,root) /etc/rc.d/init.d/nrpe
%dir %attr(775,root,nagios) /var/run/nrpe

%files plugin
%defattr(644,root,root,755)
%attr(640,root,nagios) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/plugins/nrpe.cfg
%attr(755,root,root) %{_plugindir}/check_nrpe
