#!/bin/bash
# build-rpm.sh — 把 pve-port-kernel 构建成 RPM 包
#
# 用法：
#   ./build-rpm.sh [x86_64|aarch64|riscv64] [--no-deps] [--prep-only] [--srpm-only]
#
# 产出：
#   _rpmbuild/RPMS/<arch>/pve-kernel-<KVNAME>-*.rpm
#   _rpmbuild/RPMS/<arch>/pve-headers-<KVNAME>-*.rpm
#   _rpmbuild/RPMS/<arch>/pve-kernel-libc-dev-*.rpm
#   _rpmbuild/RPMS/<arch>/linux-tools-6.6-*.rpm
#   _rpmbuild/SRPMS/pve-kernel-*.src.rpm
#
# 前置条件：
#   - openEuler / Fedora / CentOS Stream 系统
#   - dnf install rpm-build rpmdevtools gcc make bc bison flex ...
#   - git submodule update --init --depth=1（拉取 linux/ 和 zfs/）

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# ======================================================================
# 默认参数
# ======================================================================
BUILD_ARCH=""
DO_DEPS=1
PREP_ONLY=0
SRPM_ONLY=0

# ======================================================================
# 解析参数
# ======================================================================
for arg in "$@"; do
    case "$arg" in
        x86_64|amd64)       BUILD_ARCH="x86_64" ;;
        aarch64|arm64)      BUILD_ARCH="aarch64" ;;
        riscv64)            BUILD_ARCH="riscv64" ;;
        loongarch64|loong64) BUILD_ARCH="loongarch64" ;;
        --no-deps)          DO_DEPS=0 ;;
        --prep-only)        PREP_ONLY=1 ;;
        --srpm-only)        SRPM_ONLY=1 ;;
        --clean)
            echo "Cleaning _rpmbuild/"
            rm -rf "$SCRIPT_DIR/_rpmbuild"
            exit 0
            ;;
        -h|--help)
            echo "Usage: $0 [x86_64|aarch64|riscv64|loongarch64] [--no-deps] [--prep-only] [--srpm-only] [--clean]"
            echo ""
            echo "Options:"
            echo "  x86_64|aarch64|riscv64|loongarch64  Target architecture (default: host arch)"
            echo "  --no-deps               Skip installing build dependencies"
            echo "  --prep-only             Only prepare source tarball, skip rpmbuild"
            echo "  --srpm-only             Build SRPM only (no binary RPMs)"
            echo "  --clean                 Remove build directory and exit"
            exit 0
            ;;
        *)
            echo "Unknown option: $arg" >&2
            exit 1
            ;;
    esac
done

# 默认使用本机架构
if [[ -z "$BUILD_ARCH" ]]; then
    BUILD_ARCH="$(uname -m)"
fi

echo "==> Target architecture: $BUILD_ARCH"

# ======================================================================
# 从 spec 读取版本信息
# ======================================================================
SPEC_FILE="$SCRIPT_DIR/pve-kernel.spec"
if [[ ! -f "$SPEC_FILE" ]]; then
    echo "ERROR: pve-kernel.spec not found" >&2
    exit 1
fi

KERNEL_VERSION=$(awk '/%global kernel_major/ {maj=$3} /%global kernel_minor/ {min=$3} /%global kernel_patch/ {pat=$3} END {print maj"."min"."pat}' "$SPEC_FILE")
PKG_RELEASE=$(awk '/%global pkg_release/ {print $3}' "$SPEC_FILE")
PKG_DISTRO=$(awk '/%global pkg_distro/ {print $3}' "$SPEC_FILE")
KVNAME="${KERNEL_VERSION}-${PKG_RELEASE}-${PKG_DISTRO}"

echo "==> Kernel version: $KERNEL_VERSION"
echo "==> Package release: $PKG_RELEASE"
echo "==> KVNAME: $KVNAME"

# ======================================================================
# 工作目录
# ======================================================================
TOPDIR="$SCRIPT_DIR/_rpmbuild"
SOURCES_DIR="$TOPDIR/SOURCES"
SPECS_DIR="$TOPDIR/SPECS"
BUILD_DIR="$TOPDIR/BUILD"
BUILDROOT_DIR="$TOPDIR/BUILDROOT"
RPMS_DIR="$TOPDIR/RPMS"
SRPMS_DIR="$TOPDIR/SRPMS"

mkdir -p "$SOURCES_DIR" "$SPECS_DIR" "$BUILD_DIR" "$BUILDROOT_DIR" "$RPMS_DIR" "$SRPMS_DIR"

# ======================================================================
# Step 1: 确保 submodule 已初始化
# ======================================================================
echo "==> [1/5] Initializing git submodules"
if [[ ! -f "linux/Makefile" ]]; then
    git submodule update --init --depth=1
fi

# 验证 linux 源码存在
if [[ ! -f "linux/Makefile" ]]; then
    echo "ERROR: linux/Makefile not found. Run: git submodule update --init --depth=1 linux" >&2
    exit 1
fi

if [[ ! -f "zfs/META" ]]; then
    git submodule update --init --depth=1
fi

# 验证 linux 源码存在
if [[ ! -f "zfs/META" ]]; then
    echo "ERROR: zfs/META not found. Run: git submodule update --init --depth=1 zfs" >&2
    exit 1
fi

# ======================================================================
# Step 2: 打包源码 tarball
# ======================================================================
echo "==> [2/5] Creating source tarball"

TARBALL_NAME="pve-kernel-${KERNEL_VERSION}-${PKG_RELEASE}.tar.gz"
TARBALL_PATH="$SOURCES_DIR/$TARBALL_NAME"

if [[ -f "$TARBALL_PATH" ]]; then
    rm "$TARBALL_PATH"
fi

echo "    Creating tarball directly from source tree (this may take a while) ..."
# 直接用 tar 打包，通过 --transform 重命名顶层目录，避免中间 rsync 复制
tar -czf "$TARBALL_PATH" \
    --transform="s|^linux/|pve-kernel-${KERNEL_VERSION}-${PKG_RELEASE}/linux/|" \
    --transform="s|^zfs/|pve-kernel-${KERNEL_VERSION}-${PKG_RELEASE}/zfs/|" \
    --transform="s|^debian/|pve-kernel-${KERNEL_VERSION}-${PKG_RELEASE}/debian/|" \
    --transform="s|^scripts/|pve-kernel-${KERNEL_VERSION}-${PKG_RELEASE}/scripts/|" \
    --transform="s|^modules/|pve-kernel-${KERNEL_VERSION}-${PKG_RELEASE}/modules/|" \
    --exclude='.git' \
    --exclude='linux/.git' \
    --exclude='zfs/.git' \
    linux/ zfs/ debian/ scripts/ modules/

echo "    Created: $TARBALL_PATH ($(du -h "$TARBALL_PATH" | cut -f1))"


# 复制 spec
cp "$SPEC_FILE" "$SPECS_DIR/"

if [[ "$PREP_ONLY" == "1" ]]; then
    echo "==> Done (--prep-only). Tarball at: $TARBALL_PATH"
    exit 0
fi

# ======================================================================
# Step 3: 安装构建依赖
# ======================================================================
if [[ "$DO_DEPS" == "1" && "$SRPM_ONLY" == "0" ]]; then
    echo "==> [3/5] Installing build dependencies"
    SUDO=""
    if [[ $EUID -ne 0 ]]; then
        SUDO="sudo"
    fi

    if command -v dnf >/dev/null 2>&1; then
        $SUDO dnf builddep -y --spec "$SPEC_FILE" || {
            echo "WARNING: dnf builddep failed, trying manual install" >&2
            $SUDO dnf install -y \
                gcc gcc-c++ make bc bison flex openssl-devel elfutils-libelf-devel \
                dwarves perl-interpreter python3 rsync kmod zstd lz4 xz \
                hostname net-tools elfutils-devel numactl-devel libunwind-devel \
                libcap-devel slang-devel libzstd-devel perl-devel systemtap-sdt-devel \
                autoconf automake libtool libuuid-devel libblkid-devel \
                libtirpc-devel libaio-devel ncompress rpm-build || true
        }
    else
        echo "WARNING: dnf not found, skip dependency install" >&2
    fi
else
    echo "==> [3/5] Skip dependency install"
fi

# ======================================================================
# Step 4: rpmbuild
# ======================================================================
if [[ "$SRPM_ONLY" == "1" ]]; then
    echo "==> [4/5] Building SRPM only"
    rpmbuild \
        --define "_topdir $TOPDIR" \
        --define "_sourcedir $SOURCES_DIR" \
        --define "_specdir $SPECS_DIR" \
        --define "_builddir $BUILD_DIR" \
        --define "_buildrootdir $BUILDROOT_DIR" \
        --define "_rpmdir $RPMS_DIR" \
        --define "_srcrpmdir $SRPMS_DIR" \
        --define "_smp_mflags -j4" \
        --target "$BUILD_ARCH" \
        -bs "$SPECS_DIR/pve-kernel.spec"
else
    echo "==> [4/5] Building RPMs (this will take a long time)"
    rpmbuild \
        --define "_topdir $TOPDIR" \
        --define "_sourcedir $SOURCES_DIR" \
        --define "_specdir $SPECS_DIR" \
        --define "_builddir $BUILD_DIR" \
        --define "_buildrootdir $BUILDROOT_DIR" \
        --define "_rpmdir $RPMS_DIR" \
        --define "_srcrpmdir $SRPMS_DIR" \
        --define "_smp_mflags -j4" \
        --target "$BUILD_ARCH" \
        -ba "$SPECS_DIR/pve-kernel.spec"
fi

# ======================================================================
# Step 5: 输出结果
# ======================================================================
echo ""
echo "==> [5/5] Build complete!"
echo ""
echo "RPMs:"
find "$RPMS_DIR" -name '*.rpm' 2>/dev/null | sed 's/^/  /'
echo ""
echo "SRPMs:"
find "$SRPMS_DIR" -name '*.rpm' 2>/dev/null | sed 's/^/  /'
