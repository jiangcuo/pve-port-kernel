#!/bin/bash
# Script for parsing version information from debian/changelog
set -e
set -o pipefail

PACKAGE_VERSION=$(dpkg-parsechangelog -SVersion)
KERNEL_VER=$(echo "$PACKAGE_VERSION" | sed 's/-[^-]*$//')
PACKAGE_RELEASE=$(echo "$PACKAGE_VERSION" | sed 's/.*-//')
KERNEL_MAJMIN=$(echo "$KERNEL_VER" | cut -d. -f1-2)
LINUX_VERSION=$(echo "$KERNEL_VER" | cut -d. -f1)
LINUX_PATCHLEVEL=$(echo "$KERNEL_VER" | cut -d. -f2)
LINUX_SUBLEVEL=$(echo "$KERNEL_VER" | cut -d. -f3)

while getopts "MmnprdLh" OPTION; do
    case $OPTION in
    M)
        echo $LINUX_VERSION
        exit 0
        ;;
    m)
        echo $LINUX_PATCHLEVEL
        exit 0
        ;;
    n)
        echo $KERNEL_MAJMIN
        exit 0
        ;;
    p)
        echo $LINUX_SUBLEVEL
        exit 0
        ;;
    r)
        echo $PACKAGE_RELEASE
        exit 0
        ;;
    L)
        echo $KERNEL_VER
        exit 0
        ;;
    h)
        echo "version.sh [-Mmnprfh]"
        echo "  -M  major version"
        echo "  -m  minor version"
        echo "  -n  major.minor version"
        echo "  -p  patch version (sublevel)"
        echo "  -r  package release"
        echo "  -L  full kernel version"
        echo "  -h  this help message"
        exit 1
        ;;
    *)
        echo "Incorrect options provided"
        exit 1
        ;;
    esac
done

echo "$PACKAGE_VERSION"
