#!/bin/bash

set -e
set -x

if [[ "$(uname -s)" == 'Darwin' ]]; then
    if which pyenv > /dev/null; then
        eval "$(pyenv init -)"
    fi
    pyenv activate conan
fi

python ci_utils/print_version.py

export BITPRIM_BUILD_NUMBER="$(python ci_utils/print_version.py)"
export BITPRIM_CONAN_VERSION="${BITPRIM_BUILD_NUMBER}"
echo "${BITPRIM_BUILD_NUMBER}"
echo "${BITPRIM_CONAN_VERSION}"

if [ ! -f conan_version ]; then
    echo "Creating conan_version file"
    printf "${BITPRIM_BUILD_NUMBER}" > conan_version
fi


python build.py
