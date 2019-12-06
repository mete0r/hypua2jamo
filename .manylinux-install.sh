#!/usr/bin/env bash

set -e -x

cd /io/

# Compile wheels
for PYBIN in /opt/python/*/bin; do
    if \
#      [[ "${PYBIN}" == *"cp27"* ]] || \
       [[ "${PYBIN}" == *"cp35"* ]] || \
       [[ "${PYBIN}" == *"cp36"* ]] || \
       [[ "${PYBIN}" == *"cp37"* ]] || \
       [[ "${PYBIN}" == *"cp38"* ]]; then
        "${PYBIN}/python" setup.py bdist_wheel
        rm -rf /io/build /io/*.egg-info
    fi
done

ls -l /io/dist/

# Bundle external shared libraries into the wheels
for whl in /io/dist/hypua2jamo-*.whl; do
    auditwheel repair "$whl" -w /io/dist/
done
