#!/bin/bash

if [ -f /data/autobuild.sh ]; then
    echo "autobuild.sh exists"
else
    echo "autobuild.sh does not exist"
    exit 1
fi

bash /data/autobuild.sh $BUILD_ARCH
