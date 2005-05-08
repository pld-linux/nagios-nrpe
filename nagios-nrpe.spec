Summary:	Nagios remote plugin execution service/plugin
Summary(pl):	Demon i wtyczka zdalnego wywo³ywania wtyczek Nagios
Name:		nagios-nrpe
Version:	2.0
Release:	2.7
License:	GPL v2
Group:		Networking
Source0:	http://dl.sourceforge.net/nagios/nrpe-%{version}.tar.gz
# Source0-md5:	70ef9502a3b7e49fa520dbceabfa04d0
Source1:	nrpe.init
URL:		http://www.nagios.org/
BuildRequires:	autoconf
BuildRequires:	automake
BuildRequires:	rpmbuild(macros) >= 1.202
BuildRequires:	openssl-tools
PreReq:		nagios-common
Requires(pre):	/usr/bin/getgid
Requires(pre):	/bin/id
Requires(pre):	/usr/sbin/groupadd
Requires(pre):	/usr/sbin/useradd
Requires(post,postun):	/sbin/chkconfig
Requires:	nagios-plugins
Provides:	nagios-core
Obsoletes:	netsaint-nrpe
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_sysconfdir	/etc/nagios
%define		_datadir	%{_prefix}/share/%{name}
%define		_plugindir	%{_libdir}/nagios/plugins
%define		_localstatedir	%{_var}/log/nagios
%define		nsport		5666

%description
Nagios nrpe allows you to remotely execute plugins on other hosts
and report the plugin output back to the monitoring host.

%description -l pl
Nagios npre pozwala zdalnie uruchamiaæ wtyczki na innych hostach,
a wynik ich dzia³ania zwracaæ z powrotem do hosta monitoruj±cego.

%package plugin
Summary:	check_nrpe plugin for Nagios
Summary(pl):	Wtyczka check_nrpe dla Nagiosa
Group:		Networking
Requires:	nagios-core

%description plugin
check_nrpe plugin for Nagios. This plugin allows running plugins on
remote machines using nrpe service.

%description plugin -l pl
Wtyczka check_nrpe dla Nagiosa. Pozwala na zdalne uruchamianie
wtyczek na innych komputerach za pomoc± demona nrpe.

%prep
%setup -q -n nrpe-%{version}

%build
%{__aclocal}
%{__autoconf}

%configure \
	--with-init-dir=/etc/rc.d/init.d \
	--with-nrpe-port=%{nsport} \
	--with-nrpe-user=nagios \
	--with-nrpe-grp=nagios \
	--prefix=%{_prefix} \
	--exec-prefix=%{_sbindir} \
	--bindir=%{_sbindir} \
	--libexecdir=%{_plugindir} \
	--datadir=%{_prefix}/share/nagios \
	--sysconfdir=%{_sysconfdir} \
	--localstatedir=%{_localstatedir} 

%{__make} all

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{/etc/rc.d/init.d,%{_sysconfdir},%{_libdir}/nagios/plugins,%{_sbindir}} \
	$RPM_BUILD_ROOT%{_localstatedir}

install nrpe.cfg $RPM_BUILD_ROOT/etc/nagios/nrpe.cfg
install %{SOURCE1} $RPM_BUILD_ROOT/etc/rc.d/init.d/nrpe
install src/nrpe $RPM_BUILD_ROOT%{_sbindir}
install src/check_nrpe $RPM_BUILD_ROOT%{_plugindir}

%clean
rm -rf $RPM_BUILD_ROOT

%post
/sbin/chkconfig --add nrpe
if [ -f /var/lock/subsys/nrpe ]; then
	/etc/rc.d/init.d/nrpe restart 1>&2
fi

%preun
if [ "$1" = "0" ] ; then
	if [ -f /var/lock/subsys/nrpe ]; then
		/etc/rc.d/init.d/nrpe stop 1>&2
	fi
	/sbin/chkconfig --del nrpe
fi

%files
%defattr(644,root,root,755)
%doc Changelog LEGAL README* SECURITY
%attr(754,root,root) /etc/rc.d/init.d/nrpe
%attr(640,root,nagios) %config(noreplace) %verify(not size mtime md5) %{_sysconfdir}/nrpe.cfg
%attr(755,root,root) %{_sbindir}/nrpe

%files plugin
%defattr(644,root,root,755)
%dir %{_plugindir}
%attr(755,root,root) %{_plugindir}/*
