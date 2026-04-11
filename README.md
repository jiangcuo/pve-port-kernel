# pve-port-kernel

Because maintaining the kernel requires a significant amount of time, we directly use the OpenEuler 6.6 kernel as the default kernel for PVEPort. This kernel is adapted to a variety of ARM devices and LoongArch, supporting more hardware types than the upstream kernel.

## How to install
```bash
apt update
apt search pve-kernel|grep openeuler
apt install pve-kernel-6.6.0-openeuler #meta package.You can get latest version.
```
## How to build
```bash
bash autobuild.sh
```

## build in docker

```
docker run --rm -it -v `pwd`:/data -w /data  \
--entrypoint bash \
harbor.lierfang.com/pveport/pvebuilder:aarch64 \
./autobuild.sh aarch64
```

## Extra Module

[See this](modules/README.md)