import os
from utils import get_version

# cd ${TRAVIS_BUILD_DIR}
# git fetch --unshallow

if 'TRAVIS_BRANCH' in os.environ:
    branch = os.environ.get('TRAVIS_BRANCH')
elif 'APPVEYOR_REPO_BRANCH' in os.environ:
    branch = os.environ.get('APPVEYOR_REPO_BRANCH')

os.environ['BITPRIM_BRANCH'] = branch

if branch == 'dev':
    os.environ['BITPRIM_CONAN_CHANNEL'] = "testing"
    os.environ['BITPRIM_FULL_BUILD'] = "0"
elif branch.startswith('release'):
    os.environ['BITPRIM_CONAN_CHANNEL'] = "prerelease"
    os.environ['BITPRIM_FULL_BUILD'] = "1"
elif branch.startswith('hotfix'):
    os.environ['BITPRIM_CONAN_CHANNEL'] = "prerelease"
    os.environ['BITPRIM_FULL_BUILD'] = "1"
elif branch.startswith('feature'):
    os.environ['BITPRIM_CONAN_CHANNEL'] = branch
    os.environ['BITPRIM_FULL_BUILD'] = "0"
else:
    os.environ['BITPRIM_CONAN_CHANNEL'] = "prerelease"
    os.environ['BITPRIM_FULL_BUILD'] = "1"

# export BITPRIM_CONAN_VERSION="$(python ci_utils/print_version.py)"
version = get_version()
os.environ['BITPRIM_CONAN_VERSION'] = version
os.environ['BITPRIM_BUILD_NUMBER'] = version


# if [ ! -f conan_version ]; then
#     echo "Creating conan_version file"
#     printf "${BITPRIM_BUILD_NUMBER}" > conan_version
# fi

if not os.path.exists('conan_version'):
    print("Creating conan_version file")
    with open("conan_version", "w") as file:
        file.write(version)
