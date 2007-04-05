Summary:	Shared-disk cluster file system
Summary(pl.UTF-8):	Klastrowy system plików na współdzielonym dysku
Name:		gfs2
Version:	2.00.00
Release:	1
Epoch:		1
License:	GPL v2
Group:		Applications/System
Source0:	ftp://sources.redhat.com/pub/cluster/releases/cluster-%{version}.tar.gz
# Source0-md5:	2ef3f4ba9d3c87b50adfc9b406171085
URL:		http://sources.redhat.com/cluster/gfs/
BuildRequires:	kernel-libc-headers
BuildRequires:	libvolume_id-devel
BuildRequires:	ncurses-devel
BuildRequires:	perl-base
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_sbindir	/sbin

%description
GFS (Global File System) is a cluster file system. It allows a cluster
of computers to simultaneously use a block device that is shared
between them (with FC, iSCSI, NBD, etc...). GFS reads and writes to
the block device like a local filesystem, but also uses a lock module
to allow the computers coordinate their I/O so filesystem consistency
is maintained. One of the nifty features of GFS is perfect consistency
-- changes made to the filesystem on one machine show up immediately
on all other machines in the cluster.

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

%prep
%setup -q -n cluster-%{version}
cd %{name}

%{__perl} -pi -e 's,-Wall,%{rpmcflags} -I/usr/include/ncurses -Wall,' make/defines.mk.input
%{__perl} -pi -e 's/-O2 //' gfs_{mkfs,quota,tool}/Makefile

%build
cd %{name}
./configure \
	--libdir=%{_libdir} \
	--mandir=%{_mandir} \
	--prefix=%{_prefix} \
	--sbindir=%{_sbindir}
%{__make}

%install
rm -rf $RPM_BUILD_ROOT
cd %{name}

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(644,root,root,755)
%attr(755,root,root) %{_sbindir}/*
#%attr(754,root,root) /etc/rc.d/init.d/gfs2
%{_mandir}/man?/*
