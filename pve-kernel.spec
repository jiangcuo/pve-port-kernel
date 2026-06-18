# pve-kernel: PVE Port Kernel based on openEuler 6.6 + ZFS
#
%global kernel_major    6
%global kernel_minor    6
%global kernel_patch    0
%global kernel_version  %{kernel_major}.%{kernel_minor}.%{kernel_patch}
%global pkg_release     17
%global pkg_distro      openeuler

# 架构相关变量
%ifarch x86_64
%global ker_arch        x86_64
%global kernel_build_arch x86
%global kernel_image    bzImage
%global kernel_image_path arch/x86/boot/bzImage
%global kernel_install_file vmlinuz
%global defconfig       openeuler_defconfig
%global cross_compile   %{nil}
%global kernel_cc       gcc
%endif

%ifarch aarch64
%global ker_arch        arm64
%global kernel_build_arch arm64
%global kernel_image    Image
%global kernel_image_path arch/arm64/boot/Image
%global kernel_install_file vmlinuz
%global defconfig       openeuler_defconfig
%global cross_compile   %{nil}
%global kernel_cc       gcc
%endif

%ifarch riscv64
%global ker_arch        riscv
%global kernel_build_arch riscv
%global kernel_image    Image
%global kernel_image_path arch/riscv/boot/Image
%global kernel_install_file vmlinuz
%global defconfig       openeuler_defconfig
%global cross_compile   %{nil}
%global kernel_cc       gcc
%endif

%ifarch loongarch64
%global ker_arch        loongarch
%global kernel_build_arch loongarch
%global kernel_image    vmlinuz
%global kernel_image_path arch/loongarch/boot/vmlinuz
%global kernel_install_file vmlinuz
%global defconfig       loongson3_defconfig
%global cross_compile   %{nil}
%global kernel_cc       gcc
%endif

%global kvname          %{kernel_version}-%{pkg_release}-%{pkg_distro}
%global extraversion    -%{pkg_release}-%{pkg_distro}

Name:           pve-kernel
Version:        %{kernel_version}
Release:        %{pkg_release}%{?dist}
Summary:        PVE Port Kernel based on openEuler %{kernel_major}.%{kernel_minor}

License:        GPL-2.0-only
URL:            https://github.com/jiangcuo/pve-port-kernel
Source0:        pve-kernel-%{version}-%{pkg_release}.tar.gz

AutoReqProv:    no

%global debug_package %{nil}

BuildRequires:  gcc
BuildRequires:  gcc-c++
BuildRequires:  make
BuildRequires:  bc
BuildRequires:  bison
BuildRequires:  flex
BuildRequires:  openssl-devel
BuildRequires:  elfutils-libelf-devel
BuildRequires:  dwarves
BuildRequires:  perl-interpreter
BuildRequires:  python3
BuildRequires:  rsync
BuildRequires:  kmod
BuildRequires:  zstd
BuildRequires:  lz4
BuildRequires:  xz
BuildRequires:  hostname
BuildRequires:  net-tools
BuildRequires:  elfutils-devel
BuildRequires:  numactl-devel
BuildRequires:  libunwind-devel
BuildRequires:  libcap-devel
BuildRequires:  slang-devel
BuildRequires:  libzstd-devel
BuildRequires:  perl-devel
BuildRequires:  systemtap-sdt-devel
BuildRequires:  autoconf
BuildRequires:  automake
BuildRequires:  libtool
BuildRequires:  libuuid-devel
BuildRequires:  libblkid-devel
BuildRequires:  libtirpc-devel
BuildRequires:  libaio-devel
BuildRequires:  ncompress
BuildRequires:  libtraceevent-devel

Provides:       kernel = %{version}-%{release}
Provides:       kernel-core = %{version}-%{release}
Provides:       kernel-modules = %{version}-%{release}
Provides:       linux-image = %{version}-%{release}

%description
PVE Port Kernel %{kvname} based on openEuler %{kernel_major}.%{kernel_minor}.
Includes ZFS kernel modules and PVE-specific patches.
Supports x86_64, aarch64, loongarch64, and riscv64.

%package -n     pve-kernel-%{kernel_major}.%{kernel_minor}
Summary:        Latest PVE Port Kernel Image for the %{kernel_major}.%{kernel_minor} series
Requires:       pve-kernel = %{version}-%{release}
AutoReqProv:    no

%description -n pve-kernel-%{kernel_major}.%{kernel_minor}
This is a metapackage which will install the latest available
PVE Port kernel image from the %{kernel_major}.%{kernel_minor} series.

%package -n     pve-headers-%{kvname}
Summary:        Kernel headers for pve-kernel %{kvname}
Provides:       kernel-headers = %{version}-%{release}
AutoReqProv:    no

%description -n pve-headers-%{kvname}
Linux kernel headers for building external modules against
pve-kernel %{kvname}.

%package -n     pve-headers-%{kernel_major}.%{kernel_minor}
Summary:        Latest PVE Port Kernel Headers for the %{kernel_major}.%{kernel_minor} series
Requires:       pve-headers-%{kvname} = %{version}-%{release}
AutoReqProv:    no

%description -n pve-headers-%{kernel_major}.%{kernel_minor}
This is a metapackage which will install the kernel headers for the
latest available PVE Port kernel from the %{kernel_major}.%{kernel_minor} series.

%package -n     pve-kernel-libc-dev
Summary:        Linux kernel headers for userspace development
Provides:       kernel-headers-userspace = %{version}-%{release}
Conflicts:      kernel-headers
AutoReqProv:    no

%description -n pve-kernel-libc-dev
Linux support headers for userspace development (libc headers).

%package -n     linux-tools-%{kernel_major}.%{kernel_minor}
Summary:        Linux kernel tools (perf) for %{kernel_major}.%{kernel_minor}
Requires:       elfutils-libelf
AutoReqProv:    no

%description -n linux-tools-%{kernel_major}.%{kernel_minor}
Performance analysis tools (perf) for Linux kernel %{kernel_major}.%{kernel_minor}.

%prep
%setup -q -n pve-kernel-%{version}-%{pkg_release}

for p in $(cat debian/patches/series.linux); do
    echo "Applying linux patch: $p"
    patch -d linux -p1 < "debian/patches/$p"
done

for p in $(cat debian/patches/series.zfs); do
    echo "Applying zfs patch: $p"
    patch -d zfs -p1 < "debian/patches/$p"
done

%build
NPROC=%{?_smp_mflags}
NPROC=${NPROC:-"-j$(nproc)"}

make -C linux CC=%{kernel_cc} ARCH=%{ker_arch} %{defconfig}
cd linux
scripts/kconfig/merge_config.sh -m .config ../debian/config/common.kconfig
%ifarch x86_64
scripts/kconfig/merge_config.sh -m .config ../debian/config/amd64.kconfig
%endif
%ifarch aarch64
scripts/kconfig/merge_config.sh -m .config ../debian/config/arm64.kconfig
%endif
%ifarch loongarch64
scripts/kconfig/merge_config.sh -m .config ../debian/config/loong64.kconfig
%endif
make CC=%{kernel_cc} ARCH=%{ker_arch} olddefconfig
cd ..

make -C linux %{?_smp_mflags} \
    CC=%{kernel_cc} \
    ARCH=%{ker_arch} \
    EXTRAVERSION=%{extraversion} \
    LOCALVERSION=

cd zfs
autoreconf -fi
./configure \
    --with-config=kernel \
    --with-linux=$(realpath ../linux) \
    --with-linux-obj=$(realpath ../linux)
make %{?_smp_mflags}
cd ..

for moddir in modules/*/; do
    [ -d "$moddir" ] || continue
    modname=$(basename "$moddir")
    [ -f "$moddir/module.conf" ] || continue
    MODSRC="."
    . "$moddir/module.conf"
    modsrc="$moddir/$MODSRC"
    if [ ! -f "$modsrc/Makefile" ] && [ ! -f "$modsrc/Kbuild" ]; then
        echo "ERROR: $modsrc has no Makefile or Kbuild"
        exit 1
    fi
    echo "=== BUILD MODULE: $modname from $modsrc ==="
    make -C $(realpath linux) \
        CC=%{kernel_cc} \
        ARCH=%{ker_arch} \
        M=$(realpath "$modsrc") \
        modules
done

make -C linux/tools/perf %{?_smp_mflags} \
    prefix=/usr \
    HAVE_NO_LIBBFD=1 \
    HAVE_CPLUS_DEMANGLE_SUPPORT=1 \
    NO_LIBPYTHON=1 \
    NO_LIBPERL=1 \
    NO_LIBCRYPTO=1 \
    NO_LIBDEBUGINFOD=1 \
    NO_LIBBABELTRACE=1 \
    NO_JVMTI=1 \
    NO_LIBPFM4=1 \
    ARCH=%{ker_arch} \
    CC=%{kernel_cc} \
    PYTHON=python3 \
    NO_PERF_READ_VDSO32=1

%install
rm -rf %{buildroot}
KVNAME=%{kvname}

install -d -m 755 %{buildroot}/lib/modules/${KVNAME}
install -d -m 755 %{buildroot}/boot

install -m 644 linux/.config %{buildroot}/boot/config-${KVNAME}
install -m 644 linux/System.map %{buildroot}/boot/System.map-${KVNAME}
install -m 644 linux/%{kernel_image_path} %{buildroot}/boot/%{kernel_install_file}-${KVNAME}

make ARCH=%{ker_arch} -C linux \
    INSTALL_MOD_PATH=%{buildroot} \
    modules_install

make ARCH=%{ker_arch} -C linux \
    INSTALL_PATH=%{buildroot}/boot \
    dtbs_install 2>/dev/null || true

install -d -m 755 %{buildroot}/lib/modules/${KVNAME}/zfs
install -m 644 zfs/module/zfs.ko %{buildroot}/lib/modules/${KVNAME}/zfs/
install -m 644 zfs/module/spl.ko %{buildroot}/lib/modules/${KVNAME}/zfs/

for moddir in modules/*/; do
    [ -d "$moddir" ] || continue
    modname=$(basename "$moddir")
    [ -f "$moddir/module.conf" ] || continue
    MODSRC="."
    . "$moddir/module.conf"
    modsrc="$moddir/$MODSRC"
    install -d -m 755 %{buildroot}/lib/modules/${KVNAME}/extra/${modname}
    find "$modsrc" -name '*.ko' -exec install -m 644 {} \
        %{buildroot}/lib/modules/${KVNAME}/extra/${modname}/ \;
done

rm -rf %{buildroot}/lib/firmware

find %{buildroot}/lib/modules -name '*.ko' -print | while read f; do
    strip --strip-debug "$f"
done

/sbin/depmod -b %{buildroot} ${KVNAME}

install -d -m 755 %{buildroot}/lib/modprobe.d
(ls %{buildroot}/lib/modules/${KVNAME}/kernel/drivers/watchdog/ 2>/dev/null || true; \
 echo ipmi_watchdog.ko) | \
    sed -e 's/^/blacklist /' -e 's/\.ko$//' | sort -u \
    > %{buildroot}/lib/modprobe.d/blacklist_pve-kernel-${KVNAME}.conf

rm -f %{buildroot}/lib/modules/${KVNAME}/source
rm -f %{buildroot}/lib/modules/${KVNAME}/build

install -d -m 755 %{buildroot}/usr/src/linux-headers-${KVNAME}
install -m 644 linux/.config %{buildroot}/usr/src/linux-headers-${KVNAME}/

(
    cd linux
    find . -path './debian/*' -prune \
        -o -path './include/*' -prune \
        -o -path './scripts' -prune \
        -o -type f \( \
            -name 'Makefile*' \
            -o -name 'Kconfig*' \
            -o -name 'Kbuild*' \
            -o -name '*.sh' \
            -o -name '*.pl' \
        \) -print
    find include scripts -type f -o -type l
    find arch/%{kernel_build_arch} -maxdepth 1 -name 'Makefile*'
    find arch/%{kernel_build_arch} -name module.lds -o -name Kbuild.platforms -o -name Platform
    find $(find arch/%{kernel_build_arch} -name include -o -name scripts -type d) -type f 2>/dev/null || true
    find arch/%{kernel_build_arch}/include Module.symvers include scripts -type f
    find tools/ -name 'objtool' -type f 2>/dev/null || true
) | sort -u | rsync -a --files-from=- linux/ %{buildroot}/usr/src/linux-headers-${KVNAME}/

install -d -m 755 %{buildroot}/lib/modules/${KVNAME}
ln -sf /usr/src/linux-headers-${KVNAME} %{buildroot}/lib/modules/${KVNAME}/build

make -C linux headers_install \
    ARCH=%{kernel_build_arch} \
    INSTALL_HDR_PATH=%{buildroot}/usr
rm -rf %{buildroot}/usr/include/drm %{buildroot}/usr/include/scsi
find %{buildroot}/usr/include \( -name .install -o -name ..install.cmd \) -delete

install -d -m 755 %{buildroot}%{_bindir}
install -m 755 linux/tools/perf/perf \
    %{buildroot}%{_bindir}/perf_%{kernel_major}.%{kernel_minor}

%post
/sbin/depmod %{kvname} || true
if [ -d /etc/kernel/postinst.d ]; then
    run-parts --verbose --exit-on-error \
        --arg=%{kvname} \
        --arg=/boot/%{kernel_install_file}-%{kvname} \
        /etc/kernel/postinst.d || true
fi

%postun
if [ "$1" = "0" ]; then
    if [ -d /etc/kernel/postrm.d ]; then
        run-parts --verbose \
            --arg=%{kvname} \
            --arg=/boot/%{kernel_install_file}-%{kvname} \
            /etc/kernel/postrm.d || true
    fi
    rm -f /boot/initrd.img-%{kvname}
    rm -f /boot/initrd.img-%{kvname}.bak
    rm -f /var/lib/initramfs-tools/%{kvname}
fi

%files
%defattr(-,root,root,-)
/boot/config-%{kvname}
/boot/System.map-%{kvname}
/boot/%{kernel_install_file}-%{kvname}
/lib/modules/%{kvname}/
%exclude /lib/modules/%{kvname}/build
/lib/modprobe.d/blacklist_pve-kernel-%{kvname}.conf

%files -n pve-kernel-%{kernel_major}.%{kernel_minor}
# meta package, no files

%files -n pve-headers-%{kvname}
%defattr(-,root,root,-)
/usr/src/linux-headers-%{kvname}/
/lib/modules/%{kvname}/build

%files -n pve-headers-%{kernel_major}.%{kernel_minor}
# meta package, no files

%files -n pve-kernel-libc-dev
%defattr(-,root,root,-)
/usr/include/*

%files -n linux-tools-%{kernel_major}.%{kernel_minor}
%defattr(-,root,root,-)
%{_bindir}/perf_%{kernel_major}.%{kernel_minor}

%changelog
* Wed May 27 2026 Lierfang Team <itsupport@lierfang.com> - 6.6.0-17
- Update Linux to openeuler 6.6.0-152.0.0
- Disable CGROUP_XCU and CGROUP_DMEM

* Sat May 02 2026 Lierfang Team <itsupport@lierfang.com> - 6.6.0-16
- Update Linux to openeuler 6.6.0-150.0.0, Fix CVE-2026-31431

* Sat Apr 11 2026 Lierfang Team <itsupport@lierfang.com> - 6.6.0-15
- Add extra modules support
- Update Linux to openeuler 6.6.0-145.0.2

* Fri Mar 27 2026 Lierfang Team <itsupport@lierfang.com> - 6.6.0-14
- Update Linux to openeuler 20260327
- Update ZFS to 2.3.6
