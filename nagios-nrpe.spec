Summary:	Nagios remote plugin execution service/plugin
Summary(pl.UTF-8):	Demon i wtyczka zdalnego wywoływania wtyczek Nagios
Name:		nagios-nrpe
Version:	2.15
Release:	7
License:	GPL v2
Group:		Networking
Source0:	http://downloads.sourceforge.net/nagios/nrpe-%{version}.tar.gz
# Source0-md5:	3921ddc598312983f604541784b35a50
Source1:	nrpe.init
Source2:	nrpe-command.cfg
Source3:	%{name}.tmpfiles
Source4:	commands.cfg
Patch0:		%{name}-config.patch
Patch1:		nrpe_check_control.patch
Patch2:		CVE-2014-2913-nasty-metacharacters.patch
URL:		http://www.nagios.org/
BuildRequires:	openssl-devel
BuildRequires:	openssl-tools
BuildRequires:	rpmbuild(macros) >= 1.647
Requires(post,preun):	/sbin/chkconfig
Requires:	nagios-common
Requires:	rc-scripts >= 0.4.1.26
Provides:	nagios-core
Obsoletes:	netsaint-nrpe
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_sysconfdir	/etc/nagios
%define		_datadir	%{_prefix}/share/%{name}
%define		_plugindir	%{_libdir}/nagios/plugins
%define		_localstatedir	%{_var}/log/nagios
%define		nsport		5666

%description
NPRE (Nagios Remote Plugin Executor) is a system daemon that will
execute various Nagios plugins locally on behalf of a remote
(monitoring) host that uses the check_nrpe plugin.

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
The check_nrpe plugin is called from Nagios and makes plugin execution
requests to the NRPE daemon running on the remote host. Supports
passing command arguments to server, as well as native SSL/TLS
encryption (anonymous DH mode).

%description -n nagios-plugin-check_nrpe -l pl.UTF-8
Wtyczka check_nrpe dla Nagiosa. Pozwala na zdalne uruchamianie wtyczek
na innych komputerach za pomocą demona nrpe.

%prep
%setup -q -n nrpe-%{version}
%undos contrib/nrpe_check_control.c
%patch0 -p1
%patch1 -p1
%patch2 -p1

%build
%configure \
	--with-nrpe-port=%{nsport} \
	--with-nrpe-user=nagios \
	--with-nrpe-group=nagios \
	--enable-ssl \
	--with-ssl-lib=%{_libdir} \
	--enable-command-args

%{__make} all

%{__cc} %{rpmcppflags} %{rpmcflags} %{rpmldflags} contrib/nrpe_check_control.c -o contrib/nrpe_check_control

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{/etc/rc.d/init.d,%{_sysconfdir}/{plugins,nrpe.d},%{_libdir}/nagios/plugins,%{_sbindir}} \
	$RPM_BUILD_ROOT{%{_localstatedir},/var/run/nrpe} \
	$RPM_BUILD_ROOT%{systemdtmpfilesdir}

cp -p sample-config/nrpe.cfg $RPM_BUILD_ROOT%{_sysconfdir}/nrpe.cfg
cp -p %{SOURCE4} $RPM_BUILD_ROOT%{_sysconfdir}/nrpe.d
sed -e 's,@plugindir@,%{_plugindir},' %{SOURCE2} > $RPM_BUILD_ROOT%{_sysconfdir}/plugins/check_nrpe.cfg
install -p %{SOURCE1} $RPM_BUILD_ROOT/etc/rc.d/init.d/nrpe
install -p src/nrpe $RPM_BUILD_ROOT%{_sbindir}
install -p src/check_nrpe $RPM_BUILD_ROOT%{_plugindir}
cp -p %{SOURCE3} $RPM_BUILD_ROOT%{systemdtmpfilesdir}/%{name}.conf

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

%triggerpostun -- %{name} < 2.15-5
# skip *this* trigger on downgrade
[ $1 -le 1 ] && exit 0

# ensure there's include_dir directive
if ! grep -q '^include_dir=%{_sysconfdir}/nrpe.d' %{_sysconfdir}/nrpe.cfg; then
	echo 'include_dir=%{_sysconfdir}/nrpe.d' >> %{_sysconfdir}/nrpe.cfg
fi

# check if need to migrate
grep -q '^command\[' %{_sysconfdir}/nrpe.cfg || exit 0

# move command definitions to separate file
mv -f  %{_sysconfdir}/nrpe.d/commands.cfg{,.rpmnew}
grep '^command\['  %{_sysconfdir}/nrpe.cfg > %{_sysconfdir}/nrpe.d/commands.cfg
cp -f %{_sysconfdir}/nrpe.cfg{,.rpmsave}
sed -i -e '/^command\[/d' %{_sysconfdir}/nrpe.cfg

%service nrpe restart

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
%attr(640,root,nagios) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/nrpe.d/commands.cfg
%attr(755,root,root) %{_sbindir}/nrpe
%attr(754,root,root) /etc/rc.d/init.d/nrpe
%dir %attr(775,root,nagios) /var/run/nrpe
%{systemdtmpfilesdir}/%{name}.conf

%files -n nagios-plugin-check_nrpe
%defattr(644,root,root,755)
%attr(640,root,nagios) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/plugins/check_nrpe.cfg
%attr(755,root,root) %{_plugindir}/check_nrpe
