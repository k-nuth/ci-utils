#!/bin/bash

set -e
set -x

if [[ "$(uname -s)" == 'Darwin' ]]; then
    brew update || brew update
    brew outdated pyenv || brew upgrade pyenv
    brew install pyenv-virtualenv
    brew install cmake || true

    if which pyenv > /dev/null; then
        eval "$(pyenv init -)"
    fi

#     pyenv install 2.7.10
#     pyenv virtualenv 2.7.10 conan
    pyenv install 3.7.1
    pyenv virtualenv 3.7.1 conan
    pyenv rehash
    pyenv activate conan
fi

pip install  --upgrade pip > /dev/null

pip install conan==1.14.3 > /dev/null
pip install conan_package_tools==0.25.1 > /dev/null
pip install cpuid --upgrade > /dev/null


# pip install  --upgrade conan > /dev/null
# pip install conan==1.7.4 > /dev/null
# pip install conan==1.14.1 > /dev/null
# pip install conan_package_tools > /dev/null


conan --version
conan user



