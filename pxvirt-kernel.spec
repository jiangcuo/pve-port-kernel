# pxvirt-kernel: Pxvirt Kernel based on openEuler 6.6 + ZFS
#

%bcond_with pagesize_4k
%bcond_with pagesize_16k
%bcond_with pagesize_64k

%global selected_page_variants %[%{with pagesize_4k} + %{with pagesize_16k} + %{with pagesize_64k}]
%if %{selected_page_variants} > 1
%{error:Only one page-size variant can be selected}
%endif

%global kernel_major    6
%global kernel_minor    6
%global kernel_patch    0
%global kernel_version  %{kernel_major}.%{kernel_minor}.%{kernel_patch}
%global pkg_release     18
%global pkg_distro      openeuler

# 架构相关变量
%ifarch x86_64
%global ker_arch        x86
%global kernel_build_arch x86
%global kernel_image    bzImage
%global kernel_image_path arch/x86/boot/bzImage
%global kernel_install_file vmlinuz
%global defconfig       openeuler_defconfig
%global config_arch     amd64
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
%global config_arch     arm64
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
%global config_arch     riscv64
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
%global config_arch     loong64
%global cross_compile   %{nil}
%global kernel_cc       gcc
%endif

%if %{with pagesize_4k}
%global variant_suffix -4k
%global variant_page_size 4
%elif %{with pagesize_16k}
%global variant_suffix -16k
%global variant_page_size 16
%elif %{with pagesize_64k}
%global variant_suffix -64k
%global variant_page_size 64
%endif

%global abi_name                %{kernel_version}-%{pkg_release}-%{pkg_distro}
%global series_name             %{kernel_major}.%{kernel_minor}-%{pkg_distro}
%global extraversion            -%{pkg_release}.%{pkg_distro}.%{_target_cpu}%{?variant_suffix}
%global kvname                  %{kernel_version}%{extraversion}
%global runtime_pkg_name        pxvirt-kernel-%{abi_name}%{?variant_suffix}
%global runtime_meta_pkg_name   pxvirt-kernel-%{series_name}%{?variant_suffix}
%global headers_pkg_name        pxvirt-headers-%{abi_name}%{?variant_suffix}
%global headers_meta_pkg_name   pxvirt-headers-%{series_name}%{?variant_suffix}
%global debuginfo_pkg_name      %{runtime_pkg_name}-debuginfo

Name:           pxvirt-kernel
Version:        %{kernel_version}
Release:        %{pkg_release}%{?dist}
Summary:        Pxvirt Kernel source

License:        GPL-2.0-only
URL:            https://github.com/jiangcuo/pve-port-kernel
Source0:        pxvirt-kernel-%{version}-%{pkg_release}.tar.gz

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
BuildRequires:  python3-devel
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

%define _debuginfo_template %{nil}
%define _debuginfo_subpackages 0
%global _missing_build_ids_terminate_build 1
%global _no_recompute_build_ids 1
%undefine _include_minidebuginfo
%undefine _include_gdb_index
%undefine _unique_build_ids
%undefine _debugsource_packages
%{expand:%%global _find_debuginfo_opts %{?_find_debuginfo_opts} --keep-section '.BTF' -p '.*/%{kvname}/.*|.*/vmlinux|XXX' -o kernel-debugfiles.list}

%description
Source package for Pxvirt Kernel based on openEuler
%{kernel_major}.%{kernel_minor}. Binary kernel packages use the Pxvirt naming
scheme and are selected one variant at a time.

%package -n     %{runtime_pkg_name}
Summary:        Pxvirt Kernel %{abi_name}%{?variant_suffix}
AutoReqProv:    no
Provides:       kernel-uname-r(%{kvname})
%if %{selected_page_variants} == 0
Provides:       kernel-uname-r = %{kvname}
%endif
Provides:       kernel = %{version}-%{release}
Provides:       kernel-%{_target_cpu} = %{version}-%{release}
Provides:       kernel-core = %{version}-%{release}
Provides:       kernel-modules = %{version}-%{release}
Provides:       installonlypkg(kernel)
Provides:       linux-image = %{version}-%{release}

%description -n %{runtime_pkg_name}
Pxvirt Kernel %{kvname} based on openEuler. Includes ZFS kernel modules
and Pxvirt-specific patches.

%package -n     %{runtime_meta_pkg_name}
Summary:        Latest Pxvirt Kernel for the %{series_name}%{?variant_suffix} series
BuildArch:      noarch
Requires:       %{runtime_pkg_name} = %{version}-%{release}
AutoReqProv:    no

%description -n %{runtime_meta_pkg_name}
Metapackage for the latest Pxvirt Kernel in the
%{series_name}%{?variant_suffix} series.

%package -n     %{headers_pkg_name}
Summary:        Development files for Pxvirt Kernel %{kvname}
AutoReqProv:    no
Provides:       kernel-devel-uname-r(%{kvname})
%if %{selected_page_variants} == 0
Provides:       kernel-devel-uname-r = %{kvname}
%endif
Provides:       kernel-devel-%{_target_cpu} = %{version}-%{release}

%description -n %{headers_pkg_name}
Kernel headers and makefiles for building external modules against
Pxvirt Kernel %{kvname}.

%package -n     %{headers_meta_pkg_name}
Summary:        Latest Pxvirt Kernel headers for the %{series_name}%{?variant_suffix} series
BuildArch:      noarch
Requires:       %{headers_pkg_name} = %{version}-%{release}
AutoReqProv:    no

%description -n %{headers_meta_pkg_name}
Metapackage for the latest Pxvirt Kernel development files in the
%{series_name}%{?variant_suffix} series.

%package -n     %{debuginfo_pkg_name}
Summary:        Debug information for %{runtime_pkg_name}
AutoReq:        no
AutoProv:       yes

%description -n %{debuginfo_pkg_name}
Unstripped vmlinux and module debug information for Pxvirt Kernel %{kvname}.

%if %{selected_page_variants} == 0
%package -n     pxvirt-kernel-libc-dev
Summary:        Linux kernel headers for userspace development
Provides:       kernel-headers-userspace = %{version}-%{release}
Conflicts:      kernel-headers
AutoReqProv:    no

%description -n pxvirt-kernel-libc-dev
Linux support headers for userspace development (libc headers).

%package -n     linux-tools-%{kernel_major}.%{kernel_minor}
Summary:        Linux kernel tools (perf) for %{kernel_major}.%{kernel_minor}
Requires:       elfutils-libelf
AutoReqProv:    no

%description -n linux-tools-%{kernel_major}.%{kernel_minor}
Performance analysis tools (perf) for Linux kernel %{kernel_major}.%{kernel_minor}.
%endif

%prep
%setup -q -n pxvirt-kernel-%{version}-%{pkg_release}

for p in $(cat debian/patches/series.linux); do
    echo "Applying linux patch: $p"
    patch -d linux -p1 < "debian/patches/$p"
done

for p in $(cat debian/patches/series.zfs); do
    echo "Applying zfs patch: $p"
    patch -d zfs -p1 < "debian/patches/$p"
done

%build
%if %{selected_page_variants} > 0
%ifarch aarch64
sed -i -E \
    's/^CONFIG_ARM64_(4K|16K|64K)_PAGES=y$/CONFIG_ARM64_%{variant_page_size}K_PAGES=y/' \
    linux/arch/arm64/configs/%{defconfig}
%endif
%ifarch loongarch64
echo 'CONFIG_%{variant_page_size}KB_3LEVEL=y' >> \
    linux/arch/loongarch/configs/%{defconfig}
%endif
%endif

make -C linux \
    CC=%{kernel_cc} \
    ARCH=%{ker_arch} \
    EXTRAVERSION=%{extraversion} \
    LOCALVERSION= \
    %{defconfig}

cd linux
scripts/kconfig/merge_config.sh -m .config ../debian/config/common.kconfig
scripts/kconfig/merge_config.sh -m .config ../debian/config/%{config_arch}.kconfig
scripts/config --set-str LOCALVERSION ""
scripts/config --disable LOCALVERSION_AUTO
make CC=%{kernel_cc} ARCH=%{ker_arch} \
    EXTRAVERSION=%{extraversion} LOCALVERSION= olddefconfig
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
    make -C $(realpath linux) %{?_smp_mflags} \
        CC=%{kernel_cc} \
        ARCH=%{ker_arch} \
        EXTRAVERSION=%{extraversion} \
        LOCALVERSION= \
        M=$(realpath "$modsrc") \
        modules
done

%if %{selected_page_variants} == 0
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
%endif

%install
rm -rf %{buildroot}
KVNAME=%{kvname}

install -d -m 755 %{buildroot}/lib/modules/${KVNAME}
install -d -m 755 %{buildroot}/boot

install -m 644 linux/.config %{buildroot}/boot/config-${KVNAME}
install -m 644 linux/System.map %{buildroot}/boot/System.map-${KVNAME}
install -m 644 linux/%{kernel_image_path} %{buildroot}/boot/%{kernel_install_file}-${KVNAME}

make -C linux \
    CC=%{kernel_cc} \
    ARCH=%{ker_arch} \
    EXTRAVERSION=%{extraversion} \
    LOCALVERSION= \
    INSTALL_MOD_PATH=%{buildroot} \
    modules_install

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

find %{buildroot}/lib/modules/${KVNAME} -name '*.ko' -print > module-files.list
# find-debuginfo only processes executable ELF files. This follows the
# openEuler kernel spec flow and leaves module stripping to RPM.
xargs --no-run-if-empty chmod u+x < module-files.list

/sbin/depmod -b %{buildroot} ${KVNAME}

install -d -m 755 %{buildroot}/lib/modprobe.d
(ls %{buildroot}/lib/modules/${KVNAME}/kernel/drivers/watchdog/ 2>/dev/null || true; \
 echo ipmi_watchdog.ko) | \
    sed -e 's/^/blacklist /' -e 's/\.ko$//' | sort -u \
    > %{buildroot}/lib/modprobe.d/blacklist_pxvirt-kernel-${KVNAME}.conf

rm -f %{buildroot}/lib/modules/${KVNAME}/source
rm -f %{buildroot}/lib/modules/${KVNAME}/build

install -d -m 755 %{buildroot}/usr/src/kernels/${KVNAME}
install -m 644 linux/.config %{buildroot}/usr/src/kernels/${KVNAME}/

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
) | sort -u | rsync -a --files-from=- linux/ %{buildroot}/usr/src/kernels/${KVNAME}/

install -d -m 755 %{buildroot}/lib/modules/${KVNAME}
ln -sf /usr/src/kernels/${KVNAME} %{buildroot}/lib/modules/${KVNAME}/build

%if %{selected_page_variants} == 0
make -C linux \
    CC=%{kernel_cc} \
    ARCH=%{ker_arch} \
    EXTRAVERSION=%{extraversion} \
    LOCALVERSION= \
    INSTALL_HDR_PATH=%{buildroot}/usr \
    headers_install
rm -rf %{buildroot}/usr/include/drm %{buildroot}/usr/include/scsi
find %{buildroot}/usr/include \( -name .install -o -name ..install.cmd \) -delete

install -d -m 755 %{buildroot}%{_bindir}
install -m 755 linux/tools/perf/perf \
    %{buildroot}%{_bindir}/perf_%{kernel_major}.%{kernel_minor}
%endif

install -d -m 755 %{buildroot}/usr/lib/debug/lib/modules/${KVNAME}
install -m 755 linux/vmlinux %{buildroot}/usr/lib/debug/lib/modules/${KVNAME}/vmlinux

%post -n %{runtime_pkg_name}
# Skip during Proxmox installer
[ -e /proxmox_install_mode ] && exit 0

/sbin/depmod %{kvname} || true

# Generate initramfs (must happen before hooks sync it to ESP)
if command -v dracut >/dev/null 2>&1; then
    dracut --force /boot/initramfs-%{kvname}.img %{kvname}
fi

# Run postinst.d hooks (e.g. zz-proxmox-boot syncs kernel+initrd to ESP)
if [ -d /etc/kernel/postinst.d ]; then
    for script in /etc/kernel/postinst.d/*; do
        [ -x "$script" ] && "$script" %{kvname} /boot/%{kernel_install_file}-%{kvname} || true
    done
fi


%preun -n %{runtime_pkg_name}
# Only run on actual removal ($1=0), skip on upgrade ($1=1)
if [ "$1" = "0" ]; then
    [ -e /proxmox_install_mode ] && exit 0
    if [ -d /etc/kernel/prerm.d ]; then
        for script in /etc/kernel/prerm.d/*; do
            [ -x "$script" ] && "$script" %{kvname} /boot/%{kernel_install_file}-%{kvname} || true
        done
    fi
fi

%postun -n %{runtime_pkg_name}
# Only run on actual removal ($1=0), skip on upgrade ($1=1)
if [ "$1" = "0" ]; then
    [ -e /proxmox_install_mode ] && exit 0
    if [ -d /etc/kernel/postrm.d ]; then
        for script in /etc/kernel/postrm.d/*; do
            [ -x "$script" ] && "$script" %{kvname} /boot/%{kernel_install_file}-%{kvname} || true
        done
    fi
    rm -f /boot/initrd.img-%{kvname}
    rm -f /boot/initrd.img-%{kvname}.bak
    rm -f /boot/initramfs-%{kvname}.img
    rm -f /var/lib/initramfs-tools/%{kvname}
    # Clean up modules directory if empty
    rmdir /lib/modules/%{kvname} 2>/dev/null || true
fi

%files -n %{runtime_pkg_name}
%defattr(-,root,root,-)
/boot/config-%{kvname}
/boot/System.map-%{kvname}
/boot/%{kernel_install_file}-%{kvname}
/lib/modules/%{kvname}/
%exclude /lib/modules/%{kvname}/build
/lib/modprobe.d/blacklist_pxvirt-kernel-%{kvname}.conf

%files -n %{runtime_meta_pkg_name}
# meta package, no files

%files -n %{headers_pkg_name}
%defattr(-,root,root,-)
/usr/src/kernels/%{kvname}/
/lib/modules/%{kvname}/build

%files -n %{headers_meta_pkg_name}
# meta package, no files

%files -n %{debuginfo_pkg_name} -f kernel-debugfiles.list -f debugfiles.list

%if %{selected_page_variants} == 0
%files -n pxvirt-kernel-libc-dev
%defattr(-,root,root,-)
/usr/include/*

%files -n linux-tools-%{kernel_major}.%{kernel_minor}
%defattr(-,root,root,-)
%{_bindir}/perf_%{kernel_major}.%{kernel_minor}
%endif

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
