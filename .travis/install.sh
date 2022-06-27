#!/bin/bash

set -e
set -x

if [[ "$(uname -s)" == 'Darwin' ]]; then
    # brew update
    brew outdated pyenv || brew upgrade pyenv
    brew install pyenv-virtualenv
    brew install cmake || true

    if which pyenv > /dev/null; then
        eval "$(pyenv init -)"
    fi

    # pyenv install 3.7.1
    # pyenv virtualenv 3.7.1 conan
    pyenv install 3.8.6
    pyenv virtualenv 3.8.6 conan

    pyenv rehash
    pyenv activate conan
fi

pip install  --upgrade pip > /dev/null

pip install conan_package_tools==0.38.0 #> /dev/null
# pip install kthbuild==0.0.14 > /dev/null
pip install kthbuild --upgrade > /dev/null
pip install conan==1.49.0 > /dev/null

conan --version
conan user

uname -s

if [[ "$(uname -s)" == 'Linux' ]]; then
    # conan remote list
    conan profile new default --detect
    conan profile show default
    ls ~/.conan
    ls ~/.conan/profiles
    cat ~/.conan/profiles/default
    conan profile update settings.compiler.libcxx=libstdc++11 default
    conan profile show default
fi

if [[ "$(uname -s)" == 'Darwin' ]]; then
    conan profile show default
    conan profile update settings.compiler.version=13 default
    conan profile show default
fi