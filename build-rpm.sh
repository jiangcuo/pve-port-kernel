#!/bin/bash
# build-rpm.sh - Build Pxvirt Kernel RPMs with an optional page-size variant.
#
# Usage:
#   ./build-rpm.sh --variant <4k|16k|64k> [OPTIONS]
#
# Options:
#   --variant NAME   Select exactly one page-size variant
#   --no-deps        Skip installing build dependencies
#   --prep-only      Prepare source tarball only, skip rpmbuild
#   --srpm-only      Build the canonical source RPM only
#   --clean          Remove all RPM build directories and exit
#   -h, --help       Show this help
#
# Environment:
#   BUILD_ARCH   RPM target architecture (default: uname -m)
#   JOBS         Number of parallel compile jobs (default: nproc)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

BUILD_ARCH="${BUILD_ARCH:-$(uname -m)}"
DO_DEPS=1
PREP_ONLY=0
SRPM_ONLY=0
VARIANT=""
VARIANT_SET=0
JOBS="${JOBS:-$(nproc)}"

usage() {
    sed -n '2,/^[^#]/{ /^#/s/^# \?//p }' "$0"
}

set_variant() {
    local value="$1"

    case "$value" in
        4k|16k|64k) ;;
        *)
            echo "error: invalid variant '$value' (expected 4k, 16k, or 64k)" >&2
            exit 1
            ;;
    esac
    if [[ "$VARIANT_SET" == "1" ]]; then
        echo "error: kernel variant was specified more than once" >&2
        exit 1
    fi
    VARIANT="$value"
    VARIANT_SET=1
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --variant)
            [[ $# -ge 2 ]] || { echo "error: --variant requires a value" >&2; exit 1; }
            set_variant "$2"
            shift 2
            ;;
        --no-deps)
            DO_DEPS=0
            shift
            ;;
        --prep-only)
            PREP_ONLY=1
            shift
            ;;
        --srpm-only)
            SRPM_ONLY=1
            shift
            ;;
        --clean)
            rm -rf "$SCRIPT_DIR/_rpmbuild"
            echo "Cleaned _rpmbuild/"
            exit 0
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            echo "error: unknown option: $1" >&2
            exit 1
            ;;
    esac
done

if [[ "$SRPM_ONLY" == "1" && "$VARIANT_SET" == "1" ]]; then
    echo "error: --srpm-only creates the canonical source package and cannot select a variant" >&2
    exit 1
fi

SPEC_FILE="$SCRIPT_DIR/pxvirt-kernel.spec"
[[ -f "$SPEC_FILE" ]] || { echo "error: pxvirt-kernel.spec not found" >&2; exit 1; }

KERNEL_VERSION=$(awk '/%global kernel_major/{maj=$3} /%global kernel_minor/{min=$3} /%global kernel_patch/{pat=$3} END{print maj"."min"."pat}' "$SPEC_FILE")
PKG_RELEASE=$(awk '/%global pkg_release/{print $3; exit}' "$SPEC_FILE")

if [[ "$SRPM_ONLY" == "1" ]]; then
    TOPDIR="$SCRIPT_DIR/_rpmbuild/source"
elif [[ -n "$VARIANT" ]]; then
    TOPDIR="$SCRIPT_DIR/_rpmbuild/$VARIANT"
else
    TOPDIR="$SCRIPT_DIR/_rpmbuild"
fi
SOURCES_DIR="$TOPDIR/SOURCES"
SPECS_DIR="$TOPDIR/SPECS"
BUILD_DIR="$TOPDIR/BUILD"
BUILDROOT_DIR="$TOPDIR/BUILDROOT"
RPMS_DIR="$TOPDIR/RPMS"
SRPMS_DIR="$TOPDIR/SRPMS"

mkdir -p "$SOURCES_DIR" "$SPECS_DIR" "$BUILD_DIR" "$BUILDROOT_DIR" "$RPMS_DIR" "$SRPMS_DIR"

echo "arch=$BUILD_ARCH  version=$KERNEL_VERSION  release=$PKG_RELEASE  jobs=$JOBS"
if [[ -n "$VARIANT" ]]; then
    echo "variant=$VARIANT"
fi

echo "==> [1/5] Checking submodules"
[[ -f linux/Makefile ]] || git submodule update --init --depth=1
[[ -f linux/Makefile ]] || { echo "error: linux/Makefile not found" >&2; exit 1; }
[[ -f zfs/META ]] || git submodule update --init --depth=1
[[ -f zfs/META ]] || { echo "error: zfs/META not found" >&2; exit 1; }

echo "==> [2/5] Creating source tarball"
TARBALL_NAME="pxvirt-kernel-${KERNEL_VERSION}-${PKG_RELEASE}.tar.gz"
TARBALL_PATH="$SOURCES_DIR/$TARBALL_NAME"
PREFIX="pxvirt-kernel-${KERNEL_VERSION}-${PKG_RELEASE}"

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

case "$VARIANT" in
    "") VARIANT_ARGS=() ;;
    4k) VARIANT_ARGS=(--with pagesize_4k) ;;
    16k) VARIANT_ARGS=(--with pagesize_16k) ;;
    64k) VARIANT_ARGS=(--with pagesize_64k) ;;
esac

if [[ "$SRPM_ONLY" == "1" ]]; then
    echo "==> [4/5] Building canonical SRPM"
    rpmbuild "${RPMBUILD_ARGS[@]}" -bs "$SPECS_DIR/pxvirt-kernel.spec"
elif [[ -z "$VARIANT" ]]; then
    echo "==> [4/5] Building RPMs and canonical SRPM"
    rpmbuild "${RPMBUILD_ARGS[@]}" -ba "$SPECS_DIR/pxvirt-kernel.spec"
else
    echo "==> [4/5] Building ${VARIANT} binary RPMs"
    rpmbuild "${RPMBUILD_ARGS[@]}" "${VARIANT_ARGS[@]}" -bb "$SPECS_DIR/pxvirt-kernel.spec"
fi

echo
echo "==> [5/5] Done"
if [[ -n "$VARIANT" ]]; then
    echo "Variant: $VARIANT"
fi
echo "RPMs:"
find "$RPMS_DIR" -name '*.rpm' 2>/dev/null | sort | sed 's/^/  /'
echo "SRPMs:"
find "$SRPMS_DIR" -name '*.rpm' 2>/dev/null | sort | sed 's/^/  /'
