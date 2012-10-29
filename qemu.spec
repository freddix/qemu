Summary:	QEMU CPU Emulator
Name:		qemu
Version:	1.2.0
Release:	4
License:	GPL
Group:		Applications/Emulators
Source0:	http://wiki.qemu.org/download/%{name}-%{version}.tar.bz2
# Source0-md5:	78eb1e984f4532aa9f2bdd3c127b5b61
Source10:	80-kvm.rules
Source11:	kvm-modules-load.conf
Source12:	qemu-guest-agent.service
Source13:	99-qemu-guest-agent.rules
URL:		http://wiki.qemu.org/Index.html
BuildRequires:	SDL-devel
BuildRequires:	alsa-lib-devel
BuildRequires:	bluez-libs-devel
BuildRequires:	gnutls-devel
BuildRequires:	ncurses-devel
BuildRequires:	perl-tools-pod
BuildRequires:	pkg-config
BuildRequires:	sed >= 4.0
BuildRequires:	which
BuildRequires:	xorg-libX11-devel
Requires(pre,postun):	coreutils
Requires(pre,postun):	pwdutils
Provides:	group(kvm)
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

# some PPC/SPARC boot image in ELF format
%define		_noautostrip	.*%{_datadir}/qemu/.*

%define		_libexecdir	%{_libdir}/%{name}

%define		targets		i386-softmmu i386-linux-user x86_64-softmmu x86_64-linux-user arm-softmmu arm-linux-user

%description
QEMU is a FAST! processor emulator. By using dynamic translation it
achieves a reasonnable speed while being easy to port on new host
CPUs. QEMU has two operating modes:

%package guest-agent
Summary:	QEMU guest agent
Group:		Daemons
Requires:	systemd-units

%description guest-agent
QEMU guest agent.

%prep
%setup -q

%build
./configure \
	--audio-drv-list="alsa"		\
	--cc="%{__cc}"			\
	--disable-strip			\
	--enable-mixemu			\
	--extra-cflags="%{rpmcflags}"	\
	--host-cc="%{__cc}"		\
	--interp-prefix=%{_libexecdir}	\
	--libexecdir=%{_libexecdir}	\
	--prefix=%{_prefix}		\
	--sysconfdir=%{_sysconfdir}	\
	--target-list="%{targets}"
%{__make}

%install
rm -rf $RPM_BUILD_ROOT

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT	\
	libexecdir=%{_libexecdir}

install -p -D %{SOURCE10} $RPM_BUILD_ROOT/usr/lib/udev/rules.d/80-kvm.rules
install -p -D %{SOURCE11} $RPM_BUILD_ROOT/usr/lib/modules-load.d/kvm.conf
install -p -D %{SOURCE12} $RPM_BUILD_ROOT/usr/lib/systemd/system/qemu-guest-agent.service
install -p %{SOURCE13} $RPM_BUILD_ROOT/usr/lib/udev/rules.d/99-qemu-guest-agent.rules

%clean
rm -rf $RPM_BUILD_ROOT

%pre
%groupadd -g 103 kvm
%groupadd -g 104 qemu
%useradd -u 104 -g qemu -G kvm -c "QEMU User" qemu

%postun
if [ "$1" = "0" ]; then
    %userremove qemu
    %groupremove qemu
    %groupremove kvm
fi

%files
%defattr(644,root,root,755)
%doc README qemu-doc.html qemu-tech.html
%attr(755,root,root) %{_bindir}/*
%dir %{_libexecdir}
%attr(755,root,root) %{_libexecdir}/qemu-bridge-helper
%exclude %{_bindir}/qemu-ga
%{_sysconfdir}/qemu
%config(noreplace) %verify(not md5 mtime size) /usr/lib/modules-load.d/kvm.conf
/usr/lib/udev/rules.d/80-kvm.rules
%{_datadir}/qemu

%{_mandir}/man1/qemu-img.1*
%{_mandir}/man1/qemu.1*
%{_mandir}/man1/virtfs-proxy-helper.1*
%{_mandir}/man8/qemu-nbd.8*

%files guest-agent
%attr(755,root,root) %{_bindir}/qemu-ga
/usr/lib/systemd/system/qemu-guest-agent.service
/usr/lib/udev/rules.d/99-qemu-guest-agent.rules

