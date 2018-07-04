#!/bin/bash

set -e
set -x

if [[ "$(uname -s)" == 'Darwin' ]]; then
    if which pyenv > /dev/null; then
        eval "$(pyenv init -)"
    fi
    pyenv activate conan
fi

# python ci_utils/print_version.py
# export BITPRIM_BUILD_NUMBER="$(python ci_utils/print_version.py)"
# export BITPRIM_CONAN_VERSION="${BITPRIM_BUILD_NUMBER}"
# # echo "${BITPRIM_BUILD_NUMBER}"
# # echo "${BITPRIM_CONAN_VERSION}"

# if [ ! -f conan_version ]; then
#     echo "Creating conan_version file"
#     printf "${BITPRIM_BUILD_NUMBER}" > conan_version
# fi

python ci_utils/set_envvars_and_files.py

echo $BITPRIM_CONAN_VERSION
echo $BITPRIM_CONAN_CHANNEL
echo $BITPRIM_BRANCH
echo $BITPRIM_FULL_BUILD
echo $BITPRIM_BUILD_NUMBER
cat conan_version


python build.py
