#!/bin/bash

rm -rf ~/project/poky/build/conf && TEMPLATECONF=meta-srk/conf/templates/conf-srk-tiny source ~/project/poky/oe-init-build-env ~/project/poky/build && cd ~/project/poky/meta-srk
cat ~/project/poky/build/conf/local.conf | head -n 4