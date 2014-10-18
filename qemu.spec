%define		bios_ver	1.7.5

Summary:	QEMU CPU Emulator
Name:		qemu
Version:	2.1.2
Release:	1
License:	GPL
Group:		Applications/Emulators
Source0:	http://wiki.qemu.org/download/%{name}-%{version}.tar.bz2
# Source0-md5:	0ff197c4ed4b695620bc4734e77c888f
Source1:	http://code.coreboot.org/p/seabios/downloads/get/seabios-%{bios_ver}.tar.gz
# Source1-md5:	3f1e17485ca327b245ae5938d9aa02d9
Source10:	80-kvm.rules
Source11:	kvm-modules-load.conf
Source12:	qemu-guest-agent.service
Source13:	99-qemu-guest-agent.rules
Patch0:		%{name}-sdl-disable-broken-scaling.patch
URL:		http://wiki.qemu.org/Index.html
BuildRequires:	SDL-devel
BuildRequires:	alsa-lib-devel
#BuildRequires:	bluez4-devel
BuildRequires:	gnutls-devel
BuildRequires:	iasl
BuildRequires:	libaio-devel
BuildRequires:	libseccomp-devel
BuildRequires:	ncurses-devel
BuildRequires:	perl-tools-pod
BuildRequires:	pkg-config
BuildRequires:	pulseaudio-devel
BuildRequires:	sed
BuildRequires:	which
BuildRequires:	xorg-libX11-devel
Requires(pre,postun):	coreutils
Requires(pre,postun):	pwdutils
Requires(postun):	/usr/sbin/ldconfig
Provides:	group(kvm)
Conflicts:	qemu-kvm
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

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
Requires(post,preun,postun):	systemd-units

%description guest-agent
QEMU guest agent.

%prep
%setup -q -a1
%patch0 -p1

%build
./configure \
	--extra-cflags="%{rpmcflags}"	\
	--extra-ldflags="%{rpmldflags}"	\
	--host-cc="%{__cc}"		\
	--cc="%{__cc}"			\
	--interp-prefix=%{_libexecdir}	\
	--libdir=%{_libdir}		\
	--libexecdir=%{_libexecdir}	\
	--prefix=%{_prefix}		\
	--sysconfdir=%{_sysconfdir}	\
	--audio-drv-list="alsa,sdl,pa"	\
	--disable-gtk			\
	--disable-strip			\
	--enable-linux-aio		\
	--enable-seccomp		\
	--enable-tpm			\
	--target-list="%{targets}"
%{__make}

cd seabios-%{bios_ver}
%{__make} -j1

%install
rm -rf $RPM_BUILD_ROOT

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT	\
	libexecdir=%{_libexecdir}

install -p -D %{SOURCE10} $RPM_BUILD_ROOT%{_prefix}/lib/udev/rules.d/80-kvm.rules
install -p -D %{SOURCE11} $RPM_BUILD_ROOT%{_prefix}/lib/modules-load.d/kvm.conf
install -p -D %{SOURCE12} $RPM_BUILD_ROOT%{systemdunitdir}/qemu-guest-agent.service
install -p %{SOURCE13} $RPM_BUILD_ROOT%{_prefix}/lib/udev/rules.d/99-qemu-guest-agent.rules

install seabios-%{bios_ver}/out/bios.bin $RPM_BUILD_ROOT%{_datadir}/qemu/bios.bin

%clean
rm -rf $RPM_BUILD_ROOT

%pre
%groupadd -g 103 kvm
%groupadd -g 104 qemu
%useradd -u 104 -g qemu -G kvm -c "QEMU User" qemu

%post -p /usr/sbin/ldconfig

%postun
/usr/sbin/ldconfig
if [ "$1" = "0" ]; then
    %userremove qemu
    %groupremove qemu
    %groupremove kvm
fi

%post guest-agent
%systemd_post qemu-guest-agent.service

%preun guest-agent
%systemd_preun qemu-guest-agent.service

%postun guest-agent
%systemd_postun

%files
%defattr(644,root,root,755)
%doc README qemu-doc.html qemu-tech.html
%attr(755,root,root) %{_bindir}/*
%attr(755,root,root) %ghost %{_libdir}/libcacard.so.0
%attr(755,root,root) %{_libdir}/libcacard.so.*.*.*
%dir %{_libexecdir}
%attr(755,root,root) %{_libexecdir}/qemu-bridge-helper
%exclude %{_bindir}/qemu-ga
%{_sysconfdir}/qemu
%config(noreplace) %verify(not md5 mtime size) %{_prefix}/lib/modules-load.d/kvm.conf
%{_prefix}/lib/udev/rules.d/80-kvm.rules
%{_datadir}/qemu

%{_mandir}/man1/qemu-img.1*
%{_mandir}/man1/qemu.1*
%{_mandir}/man1/virtfs-proxy-helper.1*
%{_mandir}/man8/qemu-nbd.8*

%files guest-agent
%attr(755,root,root) %{_bindir}/qemu-ga
%{systemdunitdir}/qemu-guest-agent.service
%{_prefix}/lib/udev/rules.d/99-qemu-guest-agent.rules

