#
# TODO:
#	- update patch0
#	- cleanup files section
#	- change from gfs2 to cluster
#	- move to cluster-3 (for kernels 2.6.29+)
#	- split cluster pkg to gfs2, gfs, fence, dlm, rmanager,
#	  ccs, cman, group
#	- more kernel stuff (gnbd, ...), but gnbd looks dead,
#	  use iscsi, fc, aoe, nbd or sth instead
#	- optflags
#   - fixup -n cluster package mess, subpackages, duplicate files, external libs and so on
#   - is this pkg obsolete by gfs.spec with 2.03?
# INFO:
#	- gfs2 and dlm kernel modules are in the kernel package
#	  (2.6.28.9-3 for example); gfs is the old GFS.
#
# Conditional build:
%bcond_without	dist_kernel	# without distribution kernel
%bcond_with	kernel		# don't build kernel module
%bcond_without	userspace	# don't build userspace package
%bcond_with	verbose

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
Version:	2.03.10
Release:	%{rel}
Epoch:		1
License:	GPL v2
Group:		Applications/System
Source0:	ftp://sources.redhat.com/pub/cluster/releases/cluster-%{version}.tar.gz
# Source0-md5:	379b560096e315d4b52e238a5c72ba4a
Patch0:		%{name}-install.patch
Patch1:		%{name}-kernel-2.6.28.patch
URL:		http://sources.redhat.com/cluster/gfs/
BuildRequires:	libvolume_id-devel
BuildRequires:	linux-libc-headers >= 7:2.6.20
BuildRequires:	ncurses-devel
BuildRequires:	openais-devel
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
-- changes made to the filesystem on one machine show up immediately on all
other machines in the cluster.

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

%package -n cluster
Summary:	Cluster stuff
Group:		Applications/System

%description -n cluster
The rest of the cluster stuff.

%package -n kernel%{_alt_kernel}-misc-gfs
Summary:	gfs kernel module
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

%package -n kernel%{_alt_kernel}-misc-gnbd
Summary:	gnbd kernel module
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

%prep
%setup -q -n cluster-%{version}
#patch0 -p1
%patch1 -p1

sed -i -e 's,-Wall,%{rpmcflags} -I/usr/include/ncurses -Wall,' make/defines.mk.input
sed -i -e 's/ -ggdb / %{rpmcflags} /' gfs2/libgfs2/Makefile
sed -i -e 's/ -O2 -ggdb / %{rpmcflags} /' gfs2/mkfs/Makefile
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
	--libdir=%{_libdir} \
	--mandir=%{_mandir} \
	--prefix=%{_prefix} \
	--sbindir=%{_sbindir} \
	--ncursesincdir=/usr/include/ncurses \
	--without_kernel_modules

%if %{with userspace}
%{__make}
%endif

%if %{with kernel}
export KBUILD_NOPEDANTIC=1
%build_kernel_modules -C gfs-kernel/src/gfs -m gfs
#build_kernel_modules -C gnbd-kernel/src -m gnbd
%endif

%install
rm -rf $RPM_BUILD_ROOT

%if %{with userspace}
%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT

install -d $RPM_BUILD_ROOT/etc/rc.d/init.d
mv $RPM_BUILD_ROOT/''etc/init.d/* $RPM_BUILD_ROOT/etc/rc.d/init.d
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
%attr(755,root,root) %{_sbindir}/*gfs2*
%attr(754,root,root) /etc/rc.d/init.d/gfs2
%{_mandir}/man?/*gfs2*
%{_docdir}/cluster/gfs2.txt

%files -n cluster
%defattr(644,root,root,755)
%attr(754,root,root) /etc/rc.d/init.d/cman
%attr(754,root,root) /etc/rc.d/init.d/gfs
%attr(754,root,root) /etc/rc.d/init.d/qdiskd
%attr(754,root,root) /etc/rc.d/init.d/rgmanager
%attr(754,root,root) /etc/rc.d/init.d/scsi_reserve
%attr(755,root,root) %{_libdir}/libcman.so
%attr(755,root,root) %{_libdir}/libcman.so.2
%attr(755,root,root) %{_libdir}/libcman.so.2.3
%attr(755,root,root) %{_libdir}/libdlm_lt.so
%attr(755,root,root) %{_libdir}/libdlm_lt.so.2
%attr(755,root,root) %{_libdir}/libdlm_lt.so.2.3
%attr(755,root,root) %{_libdir}/libdlm.so
%attr(755,root,root) %{_libdir}/libdlm.so.2
%attr(755,root,root) %{_libdir}/libdlm.so.2.3
%attr(755,root,root) %{_sbindir}/ccsd
%attr(755,root,root) %{_sbindir}/ccs_test
%attr(755,root,root) %{_sbindir}/ccs_tool
%attr(755,root,root) %{_sbindir}/clubufflush
%attr(755,root,root) %{_sbindir}/clufindhostname
%attr(755,root,root) %{_sbindir}/clulog
%attr(755,root,root) %{_sbindir}/clunfslock
%attr(755,root,root) %{_sbindir}/clurgmgrd
%attr(755,root,root) %{_sbindir}/clurmtabd
%attr(755,root,root) %{_sbindir}/clustat
%attr(755,root,root) %{_sbindir}/clusvcadm
%attr(755,root,root) %{_sbindir}/cman_tool
%attr(755,root,root) %{_sbindir}/dlm_controld
%attr(755,root,root) %{_sbindir}/dlm_tool
%attr(755,root,root) %{_sbindir}/fence_ack_manual
%attr(755,root,root) %{_sbindir}/fence_alom
%attr(755,root,root) %{_sbindir}/fence_apc
%attr(755,root,root) %{_sbindir}/fence_apc_snmp
%attr(755,root,root) %{_sbindir}/fence_baytech
%attr(755,root,root) %{_sbindir}/fence_bladecenter
%attr(755,root,root) %{_sbindir}/fence_brocade
%attr(755,root,root) %{_sbindir}/fence_bullpap
%attr(755,root,root) %{_sbindir}/fence_cpint
%attr(755,root,root) %{_sbindir}/fenced
%attr(755,root,root) %{_sbindir}/fence_drac
%attr(755,root,root) %{_sbindir}/fence_drac5
%attr(755,root,root) %{_sbindir}/fence_egenera
%attr(755,root,root) %{_sbindir}/fence_eps
%attr(755,root,root) %{_sbindir}/fence_gnbd
%attr(755,root,root) %{_sbindir}/fence_ibmblade
%attr(755,root,root) %{_sbindir}/fence_ifmib
%attr(755,root,root) %{_sbindir}/fence_ilo
%attr(755,root,root) %{_sbindir}/fence_ipmilan
%attr(755,root,root) %{_sbindir}/fence_ldom
%attr(755,root,root) %{_sbindir}/fence_lpar
%attr(755,root,root) %{_sbindir}/fence_mcdata
%attr(755,root,root) %{_sbindir}/fence_node
%attr(755,root,root) %{_sbindir}/fence_rackswitch
%attr(755,root,root) %{_sbindir}/fence_rps10
%attr(755,root,root) %{_sbindir}/fence_rsa
%attr(755,root,root) %{_sbindir}/fence_rsb
%attr(755,root,root) %{_sbindir}/fence_sanbox2
%attr(755,root,root) %{_sbindir}/fence_scsi
%attr(755,root,root) %{_sbindir}/fence_scsi_test
%attr(755,root,root) %{_sbindir}/fence_tool
%attr(755,root,root) %{_sbindir}/fence_virsh
%attr(755,root,root) %{_sbindir}/fence_vixel
%attr(755,root,root) %{_sbindir}/fence_vmware
%attr(755,root,root) %{_sbindir}/fence_wti
%attr(755,root,root) %{_sbindir}/fence_xcat
%attr(755,root,root) %{_sbindir}/fence_zvm
%attr(755,root,root) %{_sbindir}/fsck.gfs
%attr(755,root,root) %{_sbindir}/gfs_controld
%attr(755,root,root) %{_sbindir}/gfs_debug
%attr(755,root,root) %{_sbindir}/gfs_edit
%attr(755,root,root) %{_sbindir}/gfs_fsck
%attr(755,root,root) %{_sbindir}/gfs_grow
%attr(755,root,root) %{_sbindir}/gfs_jadd
%attr(755,root,root) %{_sbindir}/gfs_mkfs
%attr(755,root,root) %{_sbindir}/gfs_quota
%attr(755,root,root) %{_sbindir}/gfs_tool
%attr(755,root,root) %{_sbindir}/gnbd_clusterd
%attr(755,root,root) %{_sbindir}/gnbd_export
%attr(755,root,root) %{_sbindir}/gnbd_get_uid
%attr(755,root,root) %{_sbindir}/gnbd_import
%attr(755,root,root) %{_sbindir}/gnbd_monitor
%attr(755,root,root) %{_sbindir}/gnbd_recvd
%attr(755,root,root) %{_sbindir}/gnbd_serv
%attr(755,root,root) %{_sbindir}/groupd
%attr(755,root,root) %{_sbindir}/group_tool
%attr(755,root,root) %{_sbindir}/mkfs.gfs
%attr(755,root,root) %{_sbindir}/mkqdisk
%attr(755,root,root) %{_sbindir}/mount.gfs
%attr(755,root,root) %{_sbindir}/qdiskd
%attr(755,root,root) %{_sbindir}/rg_test
%attr(755,root,root) %{_sbindir}/umount.gfs
%{_datadir}/cluster/apache.metadata
%{_datadir}/cluster/apache.sh
%{_datadir}/cluster/ASEHAagent.sh
%{_datadir}/cluster/clusterfs.sh
%{_datadir}/cluster/default_event_script.sl
%{_datadir}/cluster/fs.sh
%{_datadir}/cluster/ip.sh
%{_datadir}/cluster/lvm_by_lv.sh
%{_datadir}/cluster/lvm_by_vg.sh
%{_datadir}/cluster/lvm.metadata
%{_datadir}/cluster/lvm.sh
%{_datadir}/cluster/mysql.metadata
%{_datadir}/cluster/mysql.sh
%{_datadir}/cluster/named.metadata
%{_datadir}/cluster/named.sh
%{_datadir}/cluster/netfs.sh
%{_datadir}/cluster/nfsclient.sh
%{_datadir}/cluster/nfsexport.sh
%{_datadir}/cluster/ocf-shellfuncs
%{_datadir}/cluster/openldap.metadata
%{_datadir}/cluster/openldap.sh
%{_datadir}/cluster/oracledb.sh
%{_datadir}/cluster/postgres-8.metadata
%{_datadir}/cluster/postgres-8.sh
%{_datadir}/cluster/samba.metadata
%{_datadir}/cluster/samba.sh
%{_datadir}/cluster/SAPDatabase
%{_datadir}/cluster/SAPInstance
%{_datadir}/cluster/script.sh
%{_datadir}/cluster/service.sh
%{_datadir}/cluster/smb.sh
%{_datadir}/cluster/svclib_nfslock
%{_datadir}/cluster/tomcat-5.metadata
%{_datadir}/cluster/tomcat-5.sh
%{_datadir}/cluster/utils/config-utils.sh
%{_datadir}/cluster/utils/httpd-parse-config.pl
%{_datadir}/cluster/utils/member_util.sh
%{_datadir}/cluster/utils/messages.sh
%{_datadir}/cluster/utils/ra-skelet.sh
%{_datadir}/cluster/utils/tomcat-parse-config.pl
%{_datadir}/cluster/vm.sh
%{_datadir}/fence/fencing.py
%{_datadir}/fence/telnet_ssl
%{_datadir}/snmp/mibs/powernet369.mib
%{_docdir}/cluster/COPYING.applications
%{_docdir}/cluster/COPYING.libraries
%{_docdir}/cluster/COPYRIGHT
%{_docdir}/cluster/journaling.txt
%{_docdir}/cluster/min-gfs.txt
%{_docdir}/cluster/README.licence
%{_docdir}/cluster/usage.txt
/etc/udev/rules.d/51-dlm.rules
%{_includedir}/ccs.h
%{_includedir}/libcman.h
%{_includedir}/libdlm.h
%{_libdir}/libccs.a
%{_libdir}/libcman.a
%{_libdir}/libdlm.a
%{_libdir}/libdlm_lt.a
%{_mandir}/man3/dlm_cleanup.3
%{_mandir}/man3/dlm_close_lockspace.3
%{_mandir}/man3/dlm_create_lockspace.3*
%{_mandir}/man3/dlm_dispatch.3
%{_mandir}/man3/dlm_get_fd.3
%{_mandir}/man3/dlm_lock.3*
%{_mandir}/man3/dlm_lock_wait.3
%{_mandir}/man3/dlm_ls_lock.3
%{_mandir}/man3/dlm_ls_lock_wait.3
%{_mandir}/man3/dlm_ls_lockx.3
%{_mandir}/man3/dlm_ls_pthread_init.3
%{_mandir}/man3/dlm_ls_unlock.3
%{_mandir}/man3/dlm_ls_unlock_wait.3
%{_mandir}/man3/dlm_new_lockspace.3
%{_mandir}/man3/dlm_open_lockspace.3
%{_mandir}/man3/dlm_pthread_init.3
%{_mandir}/man3/dlm_release_lockspace.3
%{_mandir}/man3/dlm_unlock.3*
%{_mandir}/man3/dlm_unlock_wait.3
%{_mandir}/man3/libdlm.3*
%{_mandir}/man5/cluster.conf.5*
%{_mandir}/man5/cman.5*
%{_mandir}/man5/qdisk.5*
%{_mandir}/man7/ccs.7*
%{_mandir}/man8/ccsd.8*
%{_mandir}/man8/ccs_test.8*
%{_mandir}/man8/ccs_tool.8*
%{_mandir}/man8/clubufflush.8*
%{_mandir}/man8/clufindhostname.8*
%{_mandir}/man8/clulog.8*
%{_mandir}/man8/clurgmgrd.8*
%{_mandir}/man8/clurmtabd.8*
%{_mandir}/man8/clustat.8*
%{_mandir}/man8/clusvcadm.8*
%{_mandir}/man8/cman_tool.8*
%{_mandir}/man8/dlm_controld.8*
%{_mandir}/man8/dlm_tool.8*
%{_mandir}/man8/fence.8*
%{_mandir}/man8/fence_ack_manual.8*
%{_mandir}/man8/fence_alom.8*
%{_mandir}/man8/fence_apc.8*
%{_mandir}/man8/fence_bladecenter.8*
%{_mandir}/man8/fence_brocade.8*
%{_mandir}/man8/fence_bullpap.8*
%{_mandir}/man8/fenced.8*
%{_mandir}/man8/fence_drac.8*
%{_mandir}/man8/fence_egenera.8*
%{_mandir}/man8/fence_eps.8*
%{_mandir}/man8/fence_gnbd.8*
%{_mandir}/man8/fence_ifmib.8*
%{_mandir}/man8/fence_ilo.8*
%{_mandir}/man8/fence_ipmilan.8*
%{_mandir}/man8/fence_ldom.8*
%{_mandir}/man8/fence_manual.8*
%{_mandir}/man8/fence_mcdata.8*
%{_mandir}/man8/fence_node.8*
%{_mandir}/man8/fence_rib.8*
%{_mandir}/man8/fence_rsa.8*
%{_mandir}/man8/fence_sanbox2.8*
%{_mandir}/man8/fence_tool.8*
%{_mandir}/man8/fence_virsh.8*
%{_mandir}/man8/fence_vixel.8*
%{_mandir}/man8/fence_vmware.8*
%{_mandir}/man8/fence_wti.8*
%{_mandir}/man8/fence_xvm.8*
%{_mandir}/man8/fence_xvmd.8*
%{_mandir}/man8/gfs.8*
%{_mandir}/man8/gfs_controld.8*
%{_mandir}/man8/gfs_edit.8
%{_mandir}/man8/gfs_fsck.8*
%{_mandir}/man8/gfs_grow.8*
%{_mandir}/man8/gfs_jadd.8*
%{_mandir}/man8/gfs_mkfs.8*
%{_mandir}/man8/gfs_mount.8*
%{_mandir}/man8/gfs_quota.8*
%{_mandir}/man8/gfs_tool.8*
%{_mandir}/man8/gnbd.8*
%{_mandir}/man8/gnbd_export.8*
%{_mandir}/man8/gnbd_import.8*
%{_mandir}/man8/gnbd_serv.8*
%{_mandir}/man8/groupd.8*
%{_mandir}/man8/group_tool.8*
%{_mandir}/man8/mkqdisk.8*
%{_mandir}/man8/qdiskd.8*
%{_prefix}/libexec/lcrso/service_cman.lcrso
%endif

%if %{with kernel}
%files -n kernel%{_alt_kernel}-misc-gfs
%defattr(644,root,root,755)
/lib/modules/%{_kernel_ver}/misc/gfs.ko*
#/lib/modules/%{_kernel_ver}/misc/gnbd.ko*
%endif
