#
# Conditional build:
#
Summary:	Nagios remote monitoring service/plugin
Summary(pl):	Demon i wtyczka zdalnego monitorowania Nagios
Name:		nrpe
Version:	2.0
Release:	1
License:	GPL v2
Group:		Networking
Source0:	http://dl.sourceforge.net/nagios/nrpe-%{version}.tar.gz
Source1:	%{name}.init
URL:		http://www.nagios.org/
BuildRequires:	autoconf
BuildRequires:	automake
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)
Requires(pre):	/usr/bin/getgid
Requires(pre):	/bin/id
Requires(pre):	/usr/sbin/groupadd
Requires(pre):	/usr/sbin/useradd
Requires(post,postun):	/sbin/chkconfig
Requires:	nagios-plugins

%define		_sysconfdir	/etc/nagios
%define		_datadir	%{_prefix}/share/%{name}
%define		_plugindir	%{_libdir}/nagios/plugins
%define		_localstatedir	%{_var}/log/nagios
%define 	nsusr		nagios
%define		nsgrp		nagios
%define		nsport		5666

%description
Nagios is a program that will monitor hosts and services on your
network. It has the ability to email or page you when a problem arises
and when a problem is resolved. Nagios is written in C and is designed
to run under Linux (and some other *NIX variants) as a background
process, intermittently running checks on various services that you
specify.

The actual service checks are performed by separate "plugin" programs
which return the status of the checks to Nagios. The plugins are
available in nagios-plugins packages.

Nagios is successor to NetSaint.

%description -l pl
Nagios to program, kt�ry monitoruje serwery oraz us�ugi w naszej
sieci. Posiada on mo�liwo�� wysy�ania informacji o wyst�pieniu oraz
rozwi�zaniu problemu. Nagios zosta� napisany w C oraz jest
zaprojektowany do pracy pod Linuksem (i niekt�rymi innymi uniksami)
jako proces pracuj�cy w tle i bezustannie wykonuj�cy pewne operacje
sprawdzaj�ce.

W�a�ciwe sprawdzanie jest wykonywane przez osobne programy
("wtyczki"), kt�re zwracaj� informacje o statusie do Nagiosa. Wtyczki
s� dost�pne na stronie w pakietach nagios-plugins.

Nagios jest nast�pc� NetSainta.

%package plugin
Summary:	check_nrpe plugin for Nagios
Summary(pl):	Wtyczka check_nrpe dla Nagiosa
Group:		Networking

%description plugin
check_nrpe plugin for Nagios. This plugin allows running plugins on
remote machines using nrpe service.

%description plugin -l pl
Wtyczka check_nrpe dla Nagiosa. Pozwala na zdalne uruchamianie
wtyczek na innych komputerach za pomoc� demona nrpe.

%prep
%setup -q

%build
%{__aclocal}
%{__autoconf}

%configure \
	--with-init-dir=/etc/rc.d/init.d \
	--with-nrpe-port=%{nsport} \
	--with-nrpe-user=%{nsusr} \
	--with-nrpe-grp=%{nsgrp} \
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
install %{SOURCE1} $RPM_BUILD_ROOT/etc/rc.d/init.d/%{name}
install src/nrpe $RPM_BUILD_ROOT%{_sbindir}
install src/check_nrpe $RPM_BUILD_ROOT%{_plugindir}

%clean
rm -rf $RPM_BUILD_ROOT

%pre
if [ -n "`getgid %{nsgrp}`" ]; then
       if [ "`getgid %{nsgrp}`" != "72" ]; then
               echo "Error: group %{nsgrp} doesn't have gid=72. Correct this before installing %{name}." 1>&2
               exit 1
       fi
else
       /usr/sbin/groupadd -g 72 -f %{nsgrp}
fi
if [ -n "`id -u %{nsusr} 2>/dev/null`" ]; then
       if [ "`id -u %{nsusr}`" != "72" ]; then
               echo "Error: user %{nsusr} doesn't have uid=72. Correct this before installing %{name}." 1>&2
               exit 1
       fi
else
       /usr/sbin/useradd -u 72 -d %{_libdir}/%{name} -s /bin/false -c "%{name} User" -g %{nsgrp} %{nsusr} 1>&2
fi

%post
/sbin/chkconfig --add %{name}
if [ -f /var/lock/subsys/%{name} ]; then
	/etc/rc.d/init.d/%{name} restart 1>&2
fi

%preun
if [ "$1" = "0" ] ; then
	if [ -f /var/lock/subsys/%{name} ]; then
		/etc/rc.d/init.d/%{name} stop 1>&2
	fi
	/sbin/chkconfig --del %{name}
fi

%postun
if [ "$1" = "0" ]; then
       /usr/sbin/userdel %{nsusr}
       /usr/sbin/groupdel %{nsgrp}
fi

%files
%defattr(644,root,root,755)
%doc Changelog LEGAL README* SECURITY
%attr(754,root,root) /etc/rc.d/init.d/%{name}
%attr(751,root,%{nsgrp}) %dir %{_sysconfdir}
%attr(644,root,%{nsgrp}) %config(noreplace) %verify(not size mtime md5) %{_sysconfdir}/nrpe.cfg
%attr(755,root,root) %{_sbindir}/nrpe

%files plugin
%defattr(644,root,root,755)
%dir %{_plugindir}
%attr(755,root,root) %{_plugindir}/*
