#!/bin/bash

set -e
set -x

if [[ "$(uname -s)" == 'Darwin' ]]; then
    if which pyenv > /dev/null; then
        eval "$(pyenv init -)"
    fi
    pyenv activate conan
fi

echo $CONAN_CHANNEL
eval $(python ci_utils/set_envvars_and_files.py)
echo $CONAN_CHANNEL

conan remote add bitprim https://api.bintray.com/conan/bitprim/bitprim || true
conan remote add kth https://api.bintray.com/conan/k-nuth/kth || true
# conan info . --only None
# conan info . --only None -s compiler=gcc -s compiler.version=5 -s compiler.libcxx=libstdc++
python ci_utils/process_conan_reqs.py
conan remove "*" -f || true
conan remote remove kth || true
conan remote remove bitprim || true

conan remote remove kthbuild_kth_temp_ || true
conan remote remove kthbuild_bitprim_temp_ || true

python build.py
