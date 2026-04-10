## Kernel information
KERNEL_MAJMIN=$(shell ./scripts/version.sh -n)
KERNEL_VER=$(shell ./scripts/version.sh -L)

## Debian package information
PKG_DISTRIBUTOR ?= PVE Port
PKG_RELEASE = $(shell ./scripts/version.sh -r)
PKG_DATE := $(shell dpkg-parsechangelog -SDate)
PKG_DATE_UTC_ISO := $(shell date -u -d '$(PKG_DATE)' +%Y-%m-%d)
PKG_GIT_VERSION := $(shell git rev-parse HEAD)

# VARIANT: optional build variant suffix, e.g. make VARIANT=16k
VARIANT ?=

### Debian package names
ifeq ($(VARIANT),)
DEB_DISTRIBUTION_FULL=$(DEB_DISTRIBUTION)
else
DEB_DISTRIBUTION_FULL=$(DEB_DISTRIBUTION)-$(VARIANT)
endif

EXTRAVERSION=-${PKG_RELEASE}-${DEB_DISTRIBUTION_FULL}
LOCALVERSION=-${PKG_RELEASE}-${DEB_DISTRIBUTION_FULL}
KVNAME=${KERNEL_VER}-${PKG_RELEASE}-${DEB_DISTRIBUTION_FULL}

PVE_KERNEL_PKG=pve-kernel-${KVNAME}
PVE_HEADER_PKG=pve-headers-${KVNAME}
PVE_USR_HEADER_PKG=pve-kernel-libc-dev
LINUX_TOOLS_PKG=linux-tools-${KERNEL_MAJMIN}
