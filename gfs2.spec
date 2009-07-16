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
BuildRequires:	perl-base
BuildRequires:	openais-devel
%if %{with dist_kernel}
BuildRequires:  kernel%{_alt_kernel}-module-build >= 3:2.6.27
%endif

BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_sbindir	/sbin

%description -n gfs2
GFS (Global File System) is a cluster file system. It allows a cluster
of computers to simultaneously use a block device that is shared
between them (with FC, iSCSI, NBD, etc...). GFS reads and writes to
the block device like a local filesystem, but also uses a lock module
to allow the computers coordinate their I/O so filesystem consistency
is maintained. One of the nifty features of GFS is perfect consistency
-- changes made to the filesystem on one machine show up immediately
on all other machines in the cluster.

%description -l pl.UTF-8 -n gfs2
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
	--ncursesincdir=%{_includedir}/ncurses \
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
mv $RPM_BUILD_ROOT/etc/init.d/* $RPM_BUILD_ROOT/etc/rc.d/init.d
%endif

%if %{with kernel}
%install_kernel_modules -m gfs-kernel/src/gfs/gfs -d misc
#install_kernel_modules -m gnbd-kernel/src/gnbd -d misc
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%if %{with userspace}
%files -n gfs2
%defattr(644,root,root,755)
%attr(755,root,root) %{_sbindir}/*gfs2*
%attr(754,root,root) /etc/rc.d/init.d/gfs2
%{_mandir}/man?/*gfs2*
/usr/share/doc/cluster/gfs2.txt

%files -n cluster
%defattr(644,root,root,755)
/etc/rc.d/init.d/cman
/etc/rc.d/init.d/gfs
/etc/rc.d/init.d/qdiskd
/etc/rc.d/init.d/rgmanager
/etc/rc.d/init.d/scsi_reserve
/etc/udev/rules.d/51-dlm.rules
%{_includedir}/ccs.h
%{_includedir}/libcman.h
%{_includedir}/libdlm.h
%{_libdir}/libccs.a
%{_libdir}/libcman.a
%{_libdir}/libcman.so
%{_libdir}/libcman.so.2
%{_libdir}/libcman.so.2.3
%{_libdir}/libdlm.a
%{_libdir}/libdlm.so
%{_libdir}/libdlm.so.2
%{_libdir}/libdlm.so.2.3
%{_libdir}/libdlm_lt.a
%{_libdir}/libdlm_lt.so
%{_libdir}/libdlm_lt.so.2
%{_libdir}/libdlm_lt.so.2.3
/usr/libexec/lcrso/service_cman.lcrso
/usr/share/cluster/ASEHAagent.sh
/usr/share/cluster/SAPDatabase
/usr/share/cluster/SAPInstance
/usr/share/cluster/apache.metadata
/usr/share/cluster/apache.sh
/usr/share/cluster/clusterfs.sh
/usr/share/cluster/default_event_script.sl
/usr/share/cluster/fs.sh
/usr/share/cluster/ip.sh
/usr/share/cluster/lvm.metadata
/usr/share/cluster/lvm.sh
/usr/share/cluster/lvm_by_lv.sh
/usr/share/cluster/lvm_by_vg.sh
/usr/share/cluster/mysql.metadata
/usr/share/cluster/mysql.sh
/usr/share/cluster/named.metadata
/usr/share/cluster/named.sh
/usr/share/cluster/netfs.sh
/usr/share/cluster/nfsclient.sh
/usr/share/cluster/nfsexport.sh
/usr/share/cluster/ocf-shellfuncs
/usr/share/cluster/openldap.metadata
/usr/share/cluster/openldap.sh
/usr/share/cluster/oracledb.sh
/usr/share/cluster/postgres-8.metadata
/usr/share/cluster/postgres-8.sh
/usr/share/cluster/samba.metadata
/usr/share/cluster/samba.sh
/usr/share/cluster/script.sh
/usr/share/cluster/service.sh
/usr/share/cluster/smb.sh
/usr/share/cluster/svclib_nfslock
/usr/share/cluster/tomcat-5.metadata
/usr/share/cluster/tomcat-5.sh
/usr/share/cluster/utils/config-utils.sh
/usr/share/cluster/utils/httpd-parse-config.pl
/usr/share/cluster/utils/member_util.sh
/usr/share/cluster/utils/messages.sh
/usr/share/cluster/utils/ra-skelet.sh
/usr/share/cluster/utils/tomcat-parse-config.pl
/usr/share/cluster/vm.sh
/usr/share/doc/cluster/COPYING.applications
/usr/share/doc/cluster/COPYING.libraries
/usr/share/doc/cluster/COPYRIGHT
/usr/share/doc/cluster/README.licence
/usr/share/doc/cluster/journaling.txt
/usr/share/doc/cluster/min-gfs.txt
/usr/share/doc/cluster/usage.txt
/usr/share/fence/fencing.py
/usr/share/fence/telnet_ssl
/usr/share/snmp/mibs/powernet369.mib
/sbin/ccs_test
/sbin/ccs_tool
/sbin/ccsd
/sbin/clubufflush
/sbin/clufindhostname
/sbin/clulog
/sbin/clunfslock
/sbin/clurgmgrd
/sbin/clurmtabd
/sbin/clustat
/sbin/clusvcadm
/sbin/cman_tool
/sbin/dlm_controld
/sbin/dlm_tool
/sbin/fence_ack_manual
/sbin/fence_alom
/sbin/fence_apc
/sbin/fence_apc_snmp
/sbin/fence_baytech
/sbin/fence_bladecenter
/sbin/fence_brocade
/sbin/fence_bullpap
/sbin/fence_cpint
/sbin/fence_drac
/sbin/fence_drac5
/sbin/fence_egenera
/sbin/fence_eps
/sbin/fence_gnbd
/sbin/fence_ibmblade
/sbin/fence_ifmib
/sbin/fence_ilo
/sbin/fence_ipmilan
/sbin/fence_ldom
/sbin/fence_lpar
/sbin/fence_mcdata
/sbin/fence_node
/sbin/fence_rackswitch
/sbin/fence_rps10
/sbin/fence_rsa
/sbin/fence_rsb
/sbin/fence_sanbox2
/sbin/fence_scsi
/sbin/fence_scsi_test
/sbin/fence_tool
/sbin/fence_virsh
/sbin/fence_vixel
/sbin/fence_vmware
/sbin/fence_wti
/sbin/fence_xcat
/sbin/fence_zvm
/sbin/fenced
/sbin/fsck.gfs
/sbin/gfs_controld
/sbin/gfs_debug
/sbin/gfs_edit
/sbin/gfs_fsck
/sbin/gfs_grow
/sbin/gfs_jadd
/sbin/gfs_mkfs
/sbin/gfs_quota
/sbin/gfs_tool
/sbin/gnbd_clusterd
/sbin/gnbd_export
/sbin/gnbd_get_uid
/sbin/gnbd_import
/sbin/gnbd_monitor
/sbin/gnbd_recvd
/sbin/gnbd_serv
/sbin/group_tool
/sbin/groupd
/sbin/mkfs.gfs
/sbin/mkqdisk
/sbin/mount.gfs
/sbin/qdiskd
/sbin/rg_test
/sbin/umount.gfs
/usr/include/ccs.h
/usr/include/libcman.h
/usr/include/libdlm.h
/usr/lib/libccs.a
/usr/lib/libcman.a
/usr/lib/libcman.so
/usr/lib/libcman.so.2
/usr/lib/libcman.so.2.3
/usr/lib/libdlm.a
/usr/lib/libdlm.so
/usr/lib/libdlm.so.2
/usr/lib/libdlm.so.2.3
/usr/lib/libdlm_lt.a
/usr/lib/libdlm_lt.so
/usr/lib/libdlm_lt.so.2
/usr/lib/libdlm_lt.so.2.3
/usr/libexec/lcrso/service_cman.lcrso
/usr/share/cluster/ASEHAagent.sh
/usr/share/cluster/SAPDatabase
/usr/share/cluster/SAPInstance
/usr/share/cluster/apache.metadata
/usr/share/cluster/apache.sh
/usr/share/cluster/clusterfs.sh
/usr/share/cluster/default_event_script.sl
/usr/share/cluster/fs.sh
/usr/share/cluster/ip.sh
/usr/share/cluster/lvm.metadata
/usr/share/cluster/lvm.sh
/usr/share/cluster/lvm_by_lv.sh
/usr/share/cluster/lvm_by_vg.sh
/usr/share/cluster/mysql.metadata
/usr/share/cluster/mysql.sh
/usr/share/cluster/named.metadata
/usr/share/cluster/named.sh
/usr/share/cluster/netfs.sh
/usr/share/cluster/nfsclient.sh
/usr/share/cluster/nfsexport.sh
/usr/share/cluster/ocf-shellfuncs
/usr/share/cluster/openldap.metadata
/usr/share/cluster/openldap.sh
/usr/share/cluster/oracledb.sh
/usr/share/cluster/postgres-8.metadata
/usr/share/cluster/postgres-8.sh
/usr/share/cluster/samba.metadata
/usr/share/cluster/samba.sh
/usr/share/cluster/script.sh
/usr/share/cluster/service.sh
/usr/share/cluster/smb.sh
/usr/share/cluster/svclib_nfslock
/usr/share/cluster/tomcat-5.metadata
/usr/share/cluster/tomcat-5.sh
/usr/share/cluster/utils/config-utils.sh
/usr/share/cluster/utils/httpd-parse-config.pl
/usr/share/cluster/utils/member_util.sh
/usr/share/cluster/utils/messages.sh
/usr/share/cluster/utils/ra-skelet.sh
/usr/share/cluster/utils/tomcat-parse-config.pl
/usr/share/cluster/vm.sh
/usr/share/doc/cluster/COPYING.applications
/usr/share/doc/cluster/COPYING.libraries
/usr/share/doc/cluster/COPYRIGHT
/usr/share/doc/cluster/README.licence
/usr/share/doc/cluster/journaling.txt
/usr/share/doc/cluster/min-gfs.txt
/usr/share/doc/cluster/usage.txt
/usr/share/fence/fencing.py
/usr/share/fence/telnet_ssl
/usr/share/man/man3/dlm_cleanup.3
/usr/share/man/man3/dlm_close_lockspace.3
/usr/share/man/man3/dlm_create_lockspace.3.gz
/usr/share/man/man3/dlm_dispatch.3
/usr/share/man/man3/dlm_get_fd.3
/usr/share/man/man3/dlm_lock.3.gz
/usr/share/man/man3/dlm_lock_wait.3
/usr/share/man/man3/dlm_ls_lock.3
/usr/share/man/man3/dlm_ls_lock_wait.3
/usr/share/man/man3/dlm_ls_lockx.3
/usr/share/man/man3/dlm_ls_pthread_init.3
/usr/share/man/man3/dlm_ls_unlock.3
/usr/share/man/man3/dlm_ls_unlock_wait.3
/usr/share/man/man3/dlm_new_lockspace.3
/usr/share/man/man3/dlm_open_lockspace.3
/usr/share/man/man3/dlm_pthread_init.3
/usr/share/man/man3/dlm_release_lockspace.3
/usr/share/man/man3/dlm_unlock.3.gz
/usr/share/man/man3/dlm_unlock_wait.3
/usr/share/man/man3/libdlm.3.gz
/usr/share/man/man5/cluster.conf.5.gz
/usr/share/man/man5/cman.5.gz
/usr/share/man/man5/qdisk.5.gz
/usr/share/man/man7/ccs.7.gz
/usr/share/man/man8/ccs_test.8.gz
/usr/share/man/man8/ccs_tool.8.gz
/usr/share/man/man8/ccsd.8.gz
/usr/share/man/man8/clubufflush.8.gz
/usr/share/man/man8/clufindhostname.8.gz
/usr/share/man/man8/clulog.8.gz
/usr/share/man/man8/clurgmgrd.8.gz
/usr/share/man/man8/clurmtabd.8.gz
/usr/share/man/man8/clustat.8.gz
/usr/share/man/man8/clusvcadm.8.gz
/usr/share/man/man8/cman_tool.8.gz
/usr/share/man/man8/dlm_controld.8.gz
/usr/share/man/man8/dlm_tool.8.gz
/usr/share/man/man8/fence.8.gz
/usr/share/man/man8/fence_ack_manual.8.gz
/usr/share/man/man8/fence_alom.8.gz
/usr/share/man/man8/fence_apc.8.gz
/usr/share/man/man8/fence_bladecenter.8.gz
/usr/share/man/man8/fence_brocade.8.gz
/usr/share/man/man8/fence_bullpap.8.gz
/usr/share/man/man8/fence_drac.8.gz
/usr/share/man/man8/fence_egenera.8.gz
/usr/share/man/man8/fence_eps.8.gz
/usr/share/man/man8/fence_gnbd.8.gz
/usr/share/man/man8/fence_ifmib.8.gz
/usr/share/man/man8/fence_ilo.8.gz
/usr/share/man/man8/fence_ipmilan.8.gz
/usr/share/man/man8/fence_ldom.8.gz
/usr/share/man/man8/fence_manual.8.gz
/usr/share/man/man8/fence_mcdata.8.gz
/usr/share/man/man8/fence_node.8.gz
/usr/share/man/man8/fence_rib.8.gz
/usr/share/man/man8/fence_rsa.8.gz
/usr/share/man/man8/fence_sanbox2.8.gz
/usr/share/man/man8/fence_tool.8.gz
/usr/share/man/man8/fence_virsh.8.gz
/usr/share/man/man8/fence_vixel.8.gz
/usr/share/man/man8/fence_vmware.8.gz
/usr/share/man/man8/fence_wti.8.gz
/usr/share/man/man8/fence_xvm.8.gz
/usr/share/man/man8/fence_xvmd.8.gz
/usr/share/man/man8/fenced.8.gz
/usr/share/man/man8/gfs.8.gz
/usr/share/man/man8/gfs_controld.8.gz
/usr/share/man/man8/gfs_edit.8
/usr/share/man/man8/gfs_fsck.8.gz
/usr/share/man/man8/gfs_grow.8.gz
/usr/share/man/man8/gfs_jadd.8.gz
/usr/share/man/man8/gfs_mkfs.8.gz
/usr/share/man/man8/gfs_mount.8.gz
/usr/share/man/man8/gfs_quota.8.gz
/usr/share/man/man8/gfs_tool.8.gz
/usr/share/man/man8/gnbd.8.gz
/usr/share/man/man8/gnbd_export.8.gz
/usr/share/man/man8/gnbd_import.8.gz
/usr/share/man/man8/gnbd_serv.8.gz
/usr/share/man/man8/group_tool.8.gz
/usr/share/man/man8/groupd.8.gz
/usr/share/man/man8/mkqdisk.8.gz
/usr/share/man/man8/qdiskd.8.gz
/usr/share/snmp/mibs/powernet369.mib
%endif

%if %{with kernel}
%files -n kernel%{_alt_kernel}-misc-gfs
/lib/modules/%{_kernel_ver}/misc/gfs.ko*
#/lib/modules/%{_kernel_ver}/misc/gnbd.ko*
%endif
