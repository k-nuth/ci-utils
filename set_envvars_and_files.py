import os
import pipes
# import random
import platform
from utils import get_version

# cd ${TRAVIS_BUILD_DIR}
# git fetch --unshallow

if 'TRAVIS_BRANCH' in os.environ:
    branch = os.environ.get('TRAVIS_BRANCH')
elif 'APPVEYOR_REPO_BRANCH' in os.environ:
    branch = os.environ.get('APPVEYOR_REPO_BRANCH')

os.environ['BITPRIM_BRANCH'] = branch       # needed by get_version()

if branch == 'dev':
    channel = "testing"
    full_build = "0"
elif branch.startswith('release'):
    channel = "prerelease"
    full_build = "1"
elif branch.startswith('hotfix'):
    channel = "prerelease"
    full_build = "1"
elif branch.startswith('feature'):
    channel = branch
    full_build = "0"
else:
    channel = "prerelease"
    full_build = "1"

# export BITPRIM_CONAN_VERSION="$(python ci_utils/print_version.py)"
version = get_version()

if not os.path.exists('conan_version'):
    # print("Creating conan_version file")
    with open("conan_version", "w") as file:
        file.write(version)

if platform.system() == "Windows":
    # export_str = "set BITPRIM_BRANCH=%s | set BITPRIM_CONAN_CHANNEL=%s | set BITPRIM_FULL_BUILD=%s | set BITPRIM_CONAN_VERSION=%s | set BITPRIM_BUILD_NUMBER=%s"
    export_str = '$Env:BITPRIM_BRANCH="%s"; $Env:set BITPRIM_CONAN_CHANNEL="%s"; $Env:BITPRIM_FULL_BUILD="%s"; $Env:BITPRIM_CONAN_VERSION="%s"; $Env:BITPRIM_BUILD_NUMBER="%s"'
    # $Env:BITPRIM_CONAN_CHANNEL = "testing"
else:
    export_str = "export BITPRIM_BRANCH=%s BITPRIM_CONAN_CHANNEL=%s BITPRIM_FULL_BUILD=%s BITPRIM_CONAN_VERSION=%s BITPRIM_BUILD_NUMBER=%s"

print(export_str % (pipes.quote(str(branch)), 
                    pipes.quote(str(channel)),
                    pipes.quote(str(full_build)),
                    pipes.quote(str(version)),
                    pipes.quote(str(version)),
     ))



