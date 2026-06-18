#!/bin/bash
# build-rpm.sh - Build pve-port-kernel as RPM packages.
#
# Usage:
#   ./build-rpm.sh [OPTIONS]
#
# Options:
#   --no-deps       Skip installing build dependencies
#   --prep-only     Prepare source tarball only, skip rpmbuild
#   --srpm-only     Build source RPM only (no binary packages)
#   --clean         Remove build directory and exit
#   -h, --help      Show this help
#
# Environment:
#   JOBS    Number of parallel compile jobs (default: nproc)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# ----------------------------------------------------------------------
# Defaults
# ----------------------------------------------------------------------
BUILD_ARCH="$(uname -m)"
DO_DEPS=1
PREP_ONLY=0
SRPM_ONLY=0
JOBS="${JOBS:-$(nproc)}"

# ----------------------------------------------------------------------
# Parse arguments
# ----------------------------------------------------------------------
for arg in "$@"; do
    case "$arg" in
        --no-deps)    DO_DEPS=0 ;;
        --prep-only)  PREP_ONLY=1 ;;
        --srpm-only)  SRPM_ONLY=1 ;;
        --clean)
            rm -rf "$SCRIPT_DIR/_rpmbuild"
            echo "Cleaned _rpmbuild/"
            exit 0
            ;;
        -h|--help)
            sed -n '2,/^[^#]/{ /^#/s/^# \?//p }' "$0"
            exit 0
            ;;
        *)
            echo "error: unknown option: $arg" >&2
            exit 1
            ;;
    esac
done

# ----------------------------------------------------------------------
# Read version from spec
# ----------------------------------------------------------------------
SPEC_FILE="$SCRIPT_DIR/pve-kernel.spec"
[[ -f "$SPEC_FILE" ]] || { echo "error: pve-kernel.spec not found" >&2; exit 1; }

KERNEL_VERSION=$(awk '/%global kernel_major/{maj=$3} /%global kernel_minor/{min=$3} /%global kernel_patch/{pat=$3} END{print maj"."min"."pat}' "$SPEC_FILE")
PKG_RELEASE=$(awk '/%global pkg_release/{print $3}' "$SPEC_FILE")
PKG_DISTRO=$(awk '/%global pkg_distro/{print $3}' "$SPEC_FILE")
KVNAME="${KERNEL_VERSION}-${PKG_RELEASE}-${PKG_DISTRO}"

echo "arch=$BUILD_ARCH  version=$KERNEL_VERSION  release=$PKG_RELEASE  jobs=$JOBS"

# ----------------------------------------------------------------------
# Build directory layout
# ----------------------------------------------------------------------
TOPDIR="$SCRIPT_DIR/_rpmbuild"
SOURCES_DIR="$TOPDIR/SOURCES"
SPECS_DIR="$TOPDIR/SPECS"
BUILD_DIR="$TOPDIR/BUILD"
BUILDROOT_DIR="$TOPDIR/BUILDROOT"
RPMS_DIR="$TOPDIR/RPMS"
SRPMS_DIR="$TOPDIR/SRPMS"

mkdir -p "$SOURCES_DIR" "$SPECS_DIR" "$BUILD_DIR" "$BUILDROOT_DIR" "$RPMS_DIR" "$SRPMS_DIR"

# ----------------------------------------------------------------------
# Step 1: Ensure submodules are available
# ----------------------------------------------------------------------
echo "==> [1/5] Checking submodules"

[[ -f "linux/Makefile" ]] || git submodule update --init --depth=1
[[ -f "linux/Makefile" ]] || { echo "error: linux/Makefile not found" >&2; exit 1; }

[[ -f "zfs/META" ]] || git submodule update --init --depth=1
[[ -f "zfs/META" ]] || { echo "error: zfs/META not found" >&2; exit 1; }

# ----------------------------------------------------------------------
# Step 2: Create source tarball
# ----------------------------------------------------------------------
echo "==> [2/5] Creating source tarball"

TARBALL_NAME="pve-kernel-${KERNEL_VERSION}-${PKG_RELEASE}.tar.gz"
TARBALL_PATH="$SOURCES_DIR/$TARBALL_NAME"
PREFIX="pve-kernel-${KERNEL_VERSION}-${PKG_RELEASE}"

rm -f "$TARBALL_PATH"

tar -czf "$TARBALL_PATH" \
    --transform="s|^linux/|${PREFIX}/linux/|" \
    --transform="s|^zfs/|${PREFIX}/zfs/|" \
    --transform="s|^debian/|${PREFIX}/debian/|" \
    --transform="s|^scripts/|${PREFIX}/scripts/|" \
    --transform="s|^modules/|${PREFIX}/modules/|" \
    --exclude='.git' \
    --exclude='linux/.git' \
    --exclude='zfs/.git' \
    linux/ zfs/ debian/ scripts/ modules/

echo "    $(du -h "$TARBALL_PATH" | cut -f1)  $TARBALL_NAME"

cp "$SPEC_FILE" "$SPECS_DIR/"

if [[ "$PREP_ONLY" == "1" ]]; then
    echo "Done (prep-only). Tarball: $TARBALL_PATH"
    exit 0
fi

# ----------------------------------------------------------------------
# Step 3: Install build dependencies
# ----------------------------------------------------------------------
if [[ "$DO_DEPS" == "1" && "$SRPM_ONLY" == "0" ]]; then
    echo "==> [3/5] Installing build dependencies"
    SUDO=""
    [[ $EUID -ne 0 ]] && SUDO="sudo"

    if command -v dnf >/dev/null 2>&1; then
        $SUDO dnf builddep -y --spec "$SPEC_FILE"
    else
        echo "error: dnf not found, cannot install dependencies" >&2
        exit 1
    fi
else
    echo "==> [3/5] Skipping dependency install"
fi

# ----------------------------------------------------------------------
# Step 4: rpmbuild
# ----------------------------------------------------------------------
RPMBUILD_ARGS=(
    --define "_topdir $TOPDIR"
    --define "_sourcedir $SOURCES_DIR"
    --define "_specdir $SPECS_DIR"
    --define "_builddir $BUILD_DIR"
    --define "_buildrootdir $BUILDROOT_DIR"
    --define "_rpmdir $RPMS_DIR"
    --define "_srcrpmdir $SRPMS_DIR"
    --define "_smp_mflags -j${JOBS}"
    --target "$BUILD_ARCH"
)

if [[ "$SRPM_ONLY" == "1" ]]; then
    echo "==> [4/5] Building SRPM"
    rpmbuild "${RPMBUILD_ARGS[@]}" -bs "$SPECS_DIR/pve-kernel.spec"
else
    echo "==> [4/5] Building RPMs"
    rpmbuild "${RPMBUILD_ARGS[@]}" -ba "$SPECS_DIR/pve-kernel.spec"
fi

# ----------------------------------------------------------------------
# Step 5: Summary
# ----------------------------------------------------------------------
echo ""
echo "==> [5/5] Done"
echo ""
echo "RPMs:"
find "$RPMS_DIR" -name '*.rpm' 2>/dev/null | sort | sed 's/^/  /'
echo ""
echo "SRPMs:"
find "$SRPMS_DIR" -name '*.rpm' 2>/dev/null | sort | sed 's/^/  /'
