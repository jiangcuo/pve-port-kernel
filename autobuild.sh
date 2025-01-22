#!/bin/bash
git submodule update --init --depth=1
debian/rules debian/control
apt install devscripts  rsync -y
yes |mk-build-deps --install --remove
rm build -rf
mkdir build && rsync -ra * .git build/
cd build
dpkg-buildpackage -b -us -uc
