# NOTE:
# - obsolete, for 3rd generation cluster see cluster.spec and gfs2-utils.spec
# - gfs2 and dlm kernel modules are in the kernel package
#   (2.6.28.9-3 for example); gfs is the old GFS.
#
# TODO:
# - more kernel stuff (gnbd, ...), but gnbd looks dead,
#   use iscsi, fc, aoe, nbd or sth instead
#
# Conditional build:
%bcond_without	dist_kernel	# without distribution kernel
%bcond_with	kernel		# build kernel module
%bcond_without	userspace	# don't build userspace package
%bcond_with	verbose		# verbose kernel module build

%if %{without kernel}
%undefine	with_dist_kernel
%endif
%if "%{_alt_kernel}" != "%{nil}"
%undefine	with_userspace
%endif
%if %{without userspace}
# nothing to be placed to debuginfo package
%define		_enable_debug_packages  0
%endif

%define		rel	1
Summary:	Shared-disk cluster file system
Summary(pl.UTF-8):	Klastrowy system plików na współdzielonym dysku
Name:		gfs2
Version:	2.03.11
Release:	%{rel}
Epoch:		1
License:	GPL v2
Group:		Applications/System
Source0:	ftp://sources.redhat.com/pub/cluster/releases/cluster-%{version}.tar.gz
# Source0-md5:	712b9f583472d1de614641bc0f4a0aaf
Patch0:		%{name}-kernel-2.6.28.patch
Patch1:		%{name}-llh.patch
Patch2:		%{name}-blkid.patch
Patch3:		%{name}-quota-nolist.patch
Patch4:		cluster-kernel.patch
URL:		http://sources.redhat.com/cluster/gfs/
BuildRequires:	libblkid-devel >= 2.16
# which exactly version merged qq_ll_next into reserved in gfs2_quota struct?
BuildRequires:	linux-libc-headers >= 7:2.6.38
BuildRequires:	ncurses-devel
BuildRequires:	perl-base
%if %{with dist_kernel}
BuildRequires:	kernel%{_alt_kernel}-module-build >= 3:2.6.27
%endif
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_sbindir	/sbin

%description
GFS (Global File System) is a cluster file system. It allows a cluster
of computers to simultaneously use a block device that is shared
between them (with FC, iSCSI, NBD, etc...). GFS reads and writes to
the block device like a local filesystem, but also uses a lock module
to allow the computers coordinate their I/O so filesystem consistency
is maintained. One of the nifty features of GFS is perfect consistency
- changes made to the filesystem on one machine show up immediately on
all other machines in the cluster.

%description -l pl.UTF-8
GFS (Global File System) to klastrowy system plików. Pozwala klastrowi
komputerów na jednoczesne korzystanie z urządzenia blokowego
dzielonego między nimi (poprzez FC, iSCSI, NBD itp.). GFS odczytuje i
zapisuje urządzenie blokowe jak lokalny system plików, ale używa
dodatkowo modułu blokującego, aby umożliwić komputerom koordynowanie
ich operacji I/O w celu zachowania spójności systemu plików. Jedną z
szykownych możliwości GFS-a jest idealna spójność - zmiany wykonane w
systemie plików na jednej maszynie natychmiast pokazują się na
wszystkich innych maszynach w klastrze.

%package -n kernel%{_alt_kernel}-misc-gfs
Summary:	gfs kernel module
Summary(pl.UTF-8):	Moduł jądra gfs
Release:	%{rel}@%{_kernel_ver_str}
Group:		Base/Kernel
Requires(post,postun):	/sbin/depmod
%if %{with dist_kernel}
%requires_releq_kernel
Requires(postun):	%releq_kernel
%endif
Provides:	kernel(gfs) = %{version}-%{rel}

%description -n kernel%{_alt_kernel}-misc-gfs
gfs kernel module.

%description -n kernel%{_alt_kernel}-misc-gfs -l pl.UTF-8
Moduł jądra gfs.

%package -n kernel%{_alt_kernel}-misc-gnbd
Summary:	gnbd kernel module
Summary(pl.UTF-8):	Moduł jądra gnbd
Release:	%{rel}@%{_kernel_ver_str}
Group:		Base/Kernel
Requires(post,postun):	/sbin/depmod
%if %{with dist_kernel}
%requires_releq_kernel
Requires(postun):	%releq_kernel
%endif
Provides:	kernel(gnbd) = %{version}-%{rel}

%description -n kernel%{_alt_kernel}-misc-gnbd
gnbd kernel module.

%description -n kernel%{_alt_kernel}-misc-gnbd -l pl.UTF-8
Moduł jądra gnbd.

%prep
%setup -q -n cluster-%{version}
%patch -P0 -p1
%patch -P1 -p1
%patch -P2 -p1
%patch -P3 -p1
%patch -P4 -p1

%{__perl} -pi -e 's/-lncurses/-lncurses -ltinfo/' gfs2/edit/Makefile

%if %{with kernel}
# gfs
sed -i -e "s,\.\./\.\./\.\.,$PWD," gfs-kernel/src/gfs/Makefile
sed -i -e "s,\$(OBJDIR),$PWD," gfs-kernel/src/gfs/Makefile
# gnbd
sed -i -e "s,\.\./\.\.,$PWD," gnbd-kernel/src/Makefile
sed -i -e "s,\$(OBJDIR),$PWD," gnbd-kernel/src/Makefile
%endif

%build
./configure \
	--cc="%{__cc}" \
	--cflags="%{rpmcflags} -Wall" \
	--ldflags="%{rpmldflags}" \
	--incdir=%{_includedir} \
	--ncursesincdir=%{_includedir}/ncurses \
	--libdir=%{_libdir} \
	--libexecdir=%{_libexecdir} \
	--mandir=%{_mandir} \
	--prefix=%{_prefix} \
	--sbindir=%{_sbindir} \
	--without_gfs \
	--without_gnbd \
	--without_kernel_modules

%if %{with userspace}
%{__make} -C %{name}
%endif

%if %{with kernel}
export KBUILD_NOPEDANTIC=1
%build_kernel_modules -C gfs-kernel/src/gfs -m gfs
#build_kernel_modules -C gnbd-kernel/src -m gnbd
%endif

%install
rm -rf $RPM_BUILD_ROOT

%if %{with userspace}
%{__make} -C %{name} install \
	DESTDIR=$RPM_BUILD_ROOT

install -d $RPM_BUILD_ROOT/etc/rc.d/init.d
%{__mv} $RPM_BUILD_ROOT/''etc/init.d/* $RPM_BUILD_ROOT/etc/rc.d/init.d
%endif

%if %{with kernel}
%install_kernel_modules -m gfs-kernel/src/gfs/gfs -d misc
#install_kernel_modules -m gnbd-kernel/src/gnbd -d misc
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%if %{with userspace}
%files
%defattr(644,root,root,755)
%attr(755,root,root) %{_sbindir}/fsck.gfs2
%attr(755,root,root) %{_sbindir}/gfs2_*
%attr(755,root,root) %{_sbindir}/mkfs.gfs2
%attr(755,root,root) %{_sbindir}/mount.gfs2
%attr(755,root,root) %{_sbindir}/umount.gfs2
%attr(754,root,root) /etc/rc.d/init.d/gfs2
%{_mandir}/man8/gfs2.8*
%{_mandir}/man8/gfs2_*.8*
%{_mandir}/man8/mkfs.gfs2.8*
%endif

%if %{with kernel}
%files -n kernel%{_alt_kernel}-misc-gfs
%defattr(644,root,root,755)
/lib/modules/%{_kernel_ver}/misc/gfs.ko*
#/lib/modules/%{_kernel_ver}/misc/gnbd.ko*
%endif
