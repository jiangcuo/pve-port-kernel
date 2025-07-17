FROM debian:trixie

RUN apt update && apt install debian-ports-archive-keyring ca-certificates nano -y

RUN rm /etc/apt/sources.list.d/*

RUN echo "deb https://mirrors.ustc.edu.cn/debian/ trixie main contrib non-free non-free-firmware" >/etc/apt/sources.list \
&& echo "deb https://mirrors.ustc.edu.cn/debian/ trixie-updates main contrib non-free non-free-firmware" >> /etc/apt/sources.list \
&& echo "deb https://mirrors.ustc.edu.cn/debian-security/ trixie-security main contrib non-free non-free-firmware" >>/etc/apt/sources.list 
#&& echo "deb [arch=loong64] https://mirrors.lzu.edu.cn/debian-ports/ sid main contrib non-free non-free-firmware" >> /etc/apt/sources.list

RUN apt update \
&& apt install qemu-user-static build-* git python-dev-is-python3 pkg-config rsync devscripts debhelper \
gcc-aarch64-linux-gnu g++-aarch64-linux-gnu \
gcc-riscv64-linux-gnu g++-riscv64-linux-gnu \
gcc-loongarch64-linux-gnu g++-loongarch64-linux-gnu -y

RUN dpkg  --add-architecture arm64 \
&&  dpkg  --add-architecture loong64 \
&&  dpkg  --add-architecture riscv64


COPY ./start.sh /

CMD ["/start.sh"]
