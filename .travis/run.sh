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

conan user
conan remote list

conan remote add kth https://knuth.jfrog.io/artifactory/api/conan/knuth || true
conan remote add kth https://knuth.jfrog.io/artifactory/api/conan/knuth || true


conan user
conan remote list

# conan info . --only None
# conan info . --only None -s compiler=gcc -s compiler.version=5 -s compiler.libcxx=libstdc++
python ci_utils/process_conan_reqs.py
conan remove "*" -f || true
conan remote remove kth || true
conan remote remove kth || true

conan remote remove kthbuild_kth_temp_ || true

conan remote add tao https://taocpp.jfrog.io/artifactory/api/conan/tao -f || true


conan profile show default

python build.py
