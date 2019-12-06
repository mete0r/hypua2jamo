#!/usr/bin/env bash

set -e -x

mkdir -p dist

docker run --rm -v "$(pwd)":/io $DOCKER_IMAGE $PRE_CMD /io/.manylinux-install.sh
