#!/bin/bash
hostarch=`dpkg-architecture  -qDEB_BUILD_ARCH`
buildarch=`dpkg-architecture  -qDEB_BUILD_ARCH`
shell_path=$(realpath $(dirname $0))
VARIANT=${VARIANT:-}

os_check(){
  if [ ! -f /etc/os-release ]; then
    echo "not debian"
    exit 1
  fi
  source /etc/os-release
  if [ "$VERSION_ID" != "13" ]; then
    echo "only debian 13 is supported"
    exit 1
  fi
}

install_deps(){
    apt update
    apt install python-dev-is-python3 rsync cross-config  -y
    apt install asciidoc flex bc bison cpio dwarves flex kmod lz4 quilt xmlto zstd -y
    apt install -y libbabeltrace-dev:$hostarch \
        libcap-dev:$hostarch \
        libdw-dev:$hostarch \
        libelf-dev:$hostarch \
        libiberty-dev:$hostarch \
        libunwind-dev:$hostarch \
        libpfm4-dev:$hostarch \
        libtraceevent-dev:$hostarch \
        libnuma-dev:$hostarch \
        libslang2-dev:$hostarch \
        libssl-dev:$hostarch \
        libzstd-dev:$hostarch \
        libperl-dev:$hostarch \
        systemtap-sdt-dev:$hostarch \
        pkg-config:$hostarch \
        libstdc++6:$hostarch
    if [ "$hostarch" != "$buildarch" ]; then
      apt install qemu-user-static  crossbuild-essential-$hostarch -y
    fi
}

prepare(){
    cd $shell_path
    git submodule update --init --depth=1
    rm -f debian/control
    debian/rules debian/control
    install_deps
    rsync -ra scripts linux  debian zfs modules  build
}

build(){
    cd $shell_path/build

    VARIANT_ARGS=""
    if [ -n "$VARIANT" ]; then
      VARIANT_ARGS="-eVARIANT=$VARIANT"
    fi
    if [ "$hostarch" == "$buildarch" ]; then
      dpkg-buildpackage -us -uc -b -nc $VARIANT_ARGS
    else
      dpkg-buildpackage -us -uc -b -nc -a$hostarch -d $VARIANT_ARGS
    fi
}

# Parse all positional arguments (supports: ./autobuild.sh loongarch64 4k)
for arg in "$@"; do
    case $arg in
        clean)
        rm build *.deb pve-kernel* -rf
        exit 0
        ;;

        aarch64)
        hostarch=arm64
        ;;

        riscv64)
        hostarch=riscv64
        ;;

        loongarch64)
        hostarch=loong64
        ;;

        x86_64)
        hostarch=amd64
        ;;

        4k)
        VARIANT=4k
        ;;

        help)
        echo "usage: $0 [clean] [aarch64|riscv64|loongarch64|x86_64] [4k|VARIANT=<suffix>]"
        echo "examples:"
        echo "  $0 aarch64              # build arm64 kernel"
        echo "  $0 loongarch64 4k       # build loongarch64 4k page-size kernel"
        echo "  VARIANT=16k $0 aarch64  # build arm64 16k page-size kernel"
        exit 1
        ;;
    esac
done

#os_check
prepare
build
