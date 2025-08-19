#!/bin/bash
hostarch=`dpkg-architecture  -qDEB_BUILD_ARCH`
buildarch=`dpkg-architecture  -qDEB_BUILD_ARCH`
shell_path=$(realpath $(dirname $0))

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

build(){
    cd $shell_path
    git submodule update --init --depth=1
    rm debian/control
    debian/rules debian/control
    apt update && apt install python-dev-is-python3 rsync cross-config  -y

    rsync -ra scripts linux  debian zfs  build
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

    cd build

    if [ "$hostarch" == "$buildarch" ]; then
      dpkg-buildpackage -us -uc -b
    else
      apt install qemu-user-static  crossbuild-essential-$hostarch -y
      dpkg-buildpackage -us -uc -b -a$hostarch -d
    fi

}

#os_check
case $1 in
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
    help)
    echo "usage: $0 [clean|arm64|riscv64|loongarch64|x86_64]"
    exit 1
    ;;
    *)
    ;;
esac


build
