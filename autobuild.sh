#!/bin/bash
hostarch=host
shell_path=$(realpath $(dirname $0))

build(){
    cd $shell_path
    apt update && apt install qemu-user-static python-dev-is-python3 rsync -y
    git submodule update --init --depth=1
    debian/rules debian/control 

    if [ "$hostarch" == "host" ]; then
        yes |mk-build-deps --install --remove
    else
        yes |mk-build-deps --install --remove --host-arch $hostarch
    fi
    rsync -ra scripts linux  debian zfs  build
    cd build
    if [ "$hostarch" == "host" ]; then
      dpkg-buildpackage -us -uc -b 
    else
      dpkg-buildpackage -us -uc -b -a$hostarch
    fi

}


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
