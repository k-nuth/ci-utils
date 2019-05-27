# from conan.packager import ConanMultiPackager
import os
import copy
import re
import platform
import importlib
import subprocess
import sys
import difflib
import tempfile
from conans import ConanFile, CMake
from conans.errors import ConanException
from conans.model.version import Version
from conans import __version__ as conan_version

from subprocess import Popen, PIPE, STDOUT


DEFAULT_ORGANIZATION_NAME = 'k-nuth'
DEFAULT_LOGIN_USERNAME = 'fpelliccioni'
DEFAULT_USERNAME = 'kth'
DEFAULT_REPOSITORY = 'kth'


def get_tempfile_name():
    return os.path.join(tempfile.gettempdir(), next(tempfile._get_candidate_names()))

def get_compilation_symbols_gcc_string_program(filename, default=None):
    ofile = filename + '.o'
    afile = filename + '.a'
    try:

        # print("get_compilation_symbols_gcc_string_program - 1")

        # g++ -D_GLIBCXX_USE_CXX11_ABI=1 -c test.cxx -o test-v2.o
        # ar cr test-v1.a test-v1.o
        # nm test-v1.a

        # g++ -D_GLIBCXX_USE_CXX11_ABI=1 -c -o ofile.o -x c++ -
        # ar cr ofile.a ofile.o
        # nm ofile.a

        p = Popen(['g++', '-D_GLIBCXX_USE_CXX11_ABI=1', '-c', '-o', ofile, '-x', 'c++', '-'], stdout=PIPE, stdin=PIPE, stderr=STDOUT)    
        # print("get_compilation_symbols_gcc_string_program - 2")

        output, _ = p.communicate(input=b'#include <string>\nstd::string foo __attribute__ ((visibility ("default")));\nstd::string bar __attribute__ ((visibility ("default")));\n')
        # print("get_compilation_symbols_gcc_string_program - 3")

        if p.returncode != 0:
            # print("get_compilation_symbols_gcc_string_program - 4")
            return default

        # print("get_compilation_symbols_gcc_string_program - 5")

        p = Popen(['ar', 'cr', afile, ofile], stdout=PIPE, stdin=PIPE, stderr=STDOUT)    

        # print("get_compilation_symbols_gcc_string_program - 6")
        output, _ = p.communicate()
        # print("get_compilation_symbols_gcc_string_program - 7")

        if p.returncode != 0:
            # print("get_compilation_symbols_gcc_string_program - 8")
            return default

        # print("get_compilation_symbols_gcc_string_program - 9")

        p = Popen(['nm', afile], stdout=PIPE, stdin=PIPE, stderr=STDOUT)    
        # print("get_compilation_symbols_gcc_string_program - 10")
        output, _ = p.communicate()
        # print("get_compilation_symbols_gcc_string_program - 11")

        if p.returncode == 0:
            # print("get_compilation_symbols_gcc_string_program - 12")
            if output:
                # print("get_compilation_symbols_gcc_string_program - 13")
                return output.decode("utf-8")

        # print("get_compilation_symbols_gcc_string_program - 14")

        return default
    except OSError as e:
        # print("get_compilation_symbols_gcc_string_program - 15")
        print(e)
        return default
    except:
        # print("get_compilation_symbols_gcc_string_program - 16")
        return default

def glibcxx_supports_cxx11_abi():
    name = get_tempfile_name()
    # print(name)
    flags = get_compilation_symbols_gcc_string_program(name)
    # print(flags)
    if flags is None:
        return False
    return "__cxx11" in flags


def get_conan_packager():
    pkg = importlib.import_module('conan.packager')
    return pkg
    # try:
    #     pkg = importlib.import_module('conan.packager')
    #     return pkg
    # except ImportError:
    #     # print("*** cpuid could not be imported")
    #     return None

def get_git_branch(default=None):
    try:
        res = subprocess.Popen(["git", "rev-parse", "--abbrev-ref", "HEAD"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, _ = res.communicate()
        # print('fer 0')

        if output:
            # print('fer 0.1')
            if res.returncode == 0:
                # print('fer 0.2')
                # print(output)
                # print(output.decode("utf-8"))
                # print(output.decode("utf-8").replace('\n', ''))
                ret = output.decode("utf-8").replace('\n', '').replace('\r', '')
                # print(ret)
                return ret
        return default
    except OSError: # as e:
        # print('fer 1')
        return default
    except:
        # print('fer 2')
        return default

def get_git_describe(default=None):
    try:
        res = subprocess.Popen(["git", "describe", "master"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, _ = res.communicate()
        if output:
            if res.returncode == 0:
                return output.decode("utf-8").replace('\n', '').replace('\r', '')
                # return output.replace('\n', '').replace('\r', '')
        return default
    except OSError: # as e:
        return default
    except:
        return default

        

def get_version_from_git_describe_no_releases(default=None, is_dev_branch=False):
    describe = get_git_describe()
    
    # print('describe')
    # print(describe)

    if describe is None:
        return None
    version = describe.split('-')[0][1:]

    if is_dev_branch:
        version_arr = version.split('.')
        if len(version_arr) != 3:
            # print('version has to be of the following format: xx.xx.xx')
            return None
        # version = "%s.%s.%s" % (version_arr[0], str(int(version_arr[1]) + 1), version_arr[2])
        version = "%s.%s.%s" % (version_arr[0], str(int(version_arr[1]) + 1), 0)

    return version

def get_version_from_git_describe(default=None, is_dev_branch=False):
    describe = get_git_describe()
    
    # print('describe')
    # print(describe)

    # if describe is None:
    #     return None

    if describe is None:
        describe = "v0.0.0-"

    version = describe.split('-')[0][1:]

    if is_dev_branch:
        # print(version)
        # print(release_branch_version_to_int(version))
        
        # print(max_release_branch())

        max_release_i, max_release_s = max_release_branch()
        
        if max_release_i is not None and max_release_i > release_branch_version_to_int(version):
            version = max_release_s

        version_arr = version.split('.')
        if len(version_arr) != 3:
            # print('version has to be of the following format: xx.xx.xx')
            return None
        # version = "%s.%s.%s" % (version_arr[0], str(int(version_arr[1]) + 1), version_arr[2])
        version = "%s.%s.%s" % (version_arr[0], str(int(version_arr[1]) + 1), 0)

    return version

def get_git_branches(default=None):
    try:
        # res = subprocess.Popen(["git", "branch", "-r"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # res = subprocess.Popen(["git", "branch"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # git ls-remote --heads origin
        # res = subprocess.Popen(["git", "ls-remote", "--heads"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        res = subprocess.Popen(["git", "ls-remote", "--heads", "origin"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, _ = res.communicate()
        if output:
            if res.returncode == 0:
                # return output.decode("utf-8").replace('\n', '').replace('\r', '')
                return output.decode("utf-8")
        return default
    except OSError: # as e:
        return default
    except:
        return default

def release_branch_version_to_int(version):
    verarr = version.split('.')
    if len(verarr) != 3:
        return None
    verstr = verarr[0].zfill(5) + verarr[1].zfill(5) + verarr[2].zfill(5)
    return int(verstr)

def release_branch_version(branch):
    version = branch.split('-')[-1]
    return (release_branch_version_to_int(version), version)

def max_release_branch(default=None):
    branches = get_git_branches()
    # print(branches)
    if branches is None:
        return False

    max = None
    max_str = None

    for line in branches.splitlines():
        line = line.strip()
        # print(line)
        # if line.startswith("origin/release-"):
        if "release-" in line: 
            veri, vers = release_branch_version(line)
            if veri is not None:
                if max is None or veri > max:
                    max = veri
                    max_str = vers

    return (max, max_str)



# def get_version_from_git_describe_clean(default=None, increment_minor=False):
#     describe = get_git_describe()
    
#     if describe is None:
#         return None
#     version = describe.split('-')[0][1:]

#     if increment_minor:
#         version_arr = version.split('.')
#         if len(version_arr) != 3:
#             # print('version has to be of the following format: xx.xx.xx')
#             return None

#         version = "%s.%s.%s" % (version_arr[0], str(int(version_arr[1]) + 1), version_arr[2])

#     return version


def copy_env_vars(env_vars):
    env_vars["KNUTH_BRANCH"] = os.getenv('KNUTH_BRANCH', '-')
    env_vars["KNUTH_CONAN_CHANNEL"] = os.getenv('KNUTH_CONAN_CHANNEL', '-')
    env_vars["KNUTH_FULL_BUILD"] = os.getenv('KNUTH_FULL_BUILD', '-')
    env_vars["KNUTH_CONAN_VERSION"] = os.getenv('KNUTH_CONAN_VERSION', '-')

def is_development_branch_internal(branch = None):
    if branch is None: 
        branch = get_branch()
        
    if branch is None: 
        return False

    # return branch == 'dev' or branch.startswith('feature')    

    if branch == 'master':
        return False
    if branch.startswith('release'):
        return False
    if branch.startswith('hotfix'):
        return False

    return True


def is_development_branch():
    branch = get_branch()
    if branch is None: 
        return False

    # return branch == 'dev' or branch.startswith('feature')    

    if branch == 'master':
        return False
    if branch.startswith('release'):
        return False
    if branch.startswith('hotfix'):
        return False

    return True


# if ($Env:APPVEYOR_REPO_BRANCH -ceq "dev") {
# +        $Env:KNUTH_CONAN_CHANNEL = "testing"
# +        $Env:KNUTH_FULL_BUILD = 0
# +      }
# +      elseif ($Env:APPVEYOR_REPO_BRANCH.StartsWith("release")) {
# +        $Env:KNUTH_CONAN_CHANNEL = "stable"
# +        $Env:KNUTH_FULL_BUILD = 1
# +      }
# +      elseif ($Env:APPVEYOR_REPO_BRANCH.StartsWith("hotfix")) {
# +        $Env:KNUTH_CONAN_CHANNEL = "stable"
# +        $Env:KNUTH_FULL_BUILD = 1
# +      }
# +      elseif ($Env:APPVEYOR_REPO_BRANCH.StartsWith("feature")) {
# +        $Env:KNUTH_CONAN_CHANNEL = $Env:APPVEYOR_REPO_BRANCH
# +        $Env:KNUTH_FULL_BUILD = 0
# +      }
# +      else {
# +        $Env:KNUTH_CONAN_CHANNEL = "stable"
# +        $Env:KNUTH_FULL_BUILD = 1
# +      }


def get_branch():
    branch = os.getenv("KNUTH_BRANCH", None)
    
    # print("branch: %s" % (branch,))

    if branch is None: 
        branch = get_git_branch()

    # print("branch: %s" % (branch,))

    return branch

# def get_branch_clean():
#     branch = os.getenv("KNUTH_BRANCH", None)
#     if branch is None: 
#         branch = get_git_branch()
#     return branch

def get_version_from_branch_name():
    branch = get_branch()

    # print("get_version_from_branch_name - branch: %s" % (branch,))

    if branch is None: 
        return None

    if branch.startswith("release-") or branch.startswith("hotfix-"):
        return branch.split('-', 1)[1]

    if branch.startswith("release_") or branch.startswith("hotfix_"):
        return branch.split('_', 1)[1]

    return None

# def get_version_from_branch_name_clean():
#     branch = get_branch_clean()

#     if branch is None: 
#         return None

#     if branch.startswith("release-") or branch.startswith("hotfix-"):
#         return branch.split('-', 1)[1]

#     if branch.startswith("release_") or branch.startswith("hotfix_"):
#         return branch.split('_', 1)[1]

#     return None


def option_on_off(option):
    return "ON" if option else "OFF"

def access_file(file_path):
    with open(file_path, 'r') as f:
        return f.read().replace('\n', '').replace('\r', '')

def get_content(file_name):
    file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', file_name)
    return access_file(file_path)

def get_content_default(file_name, default=None):
    try:
        return get_content(file_name)
    except IOError:
        return default

def get_version_from_file():
    return get_content_default('conan_version')

def get_version():
    # print("get_version()----------------------------------------------------------")
    # print("KNUTH_BRANCH:        %s" % (os.getenv("KNUTH_BRANCH", None),))
    # print("KNUTH_CONAN_CHANNEL: %s" % (os.getenv("KNUTH_CONAN_CHANNEL", None),))
    # print("KNUTH_FULL_BUILD:    %s" % (os.getenv("KNUTH_FULL_BUILD", None),))
    # print("KNUTH_CONAN_VERSION: %s" % (os.getenv("KNUTH_CONAN_VERSION", None),))

    version = get_version_from_file()

    # print('------------------------------------------------------')
    # print("version 1: %s" % (version,))

    if version is None:
        version = os.getenv("KNUTH_CONAN_VERSION", None)

    # print("version 2: %s" % (version,))
    # print("KNUTH_CONAN_VERSION: %s" % (os.getenv("KNUTH_CONAN_VERSION", None),))

    if version is None:
        version = get_version_from_branch_name()

    # print("version 3: %s" % (version,))

    if version is None:
        version = get_version_from_git_describe(None, is_development_branch())

    # print("version 4: %s" % (version,))
    # print('------------------------------------------------------')

    return version

def get_version_no_releases(default=None):
    # print("get_version()----------------------------------------------------------")
    # print("KNUTH_BRANCH:        %s" % (os.getenv("KNUTH_BRANCH", None),))
    # print("KNUTH_CONAN_CHANNEL: %s" % (os.getenv("KNUTH_CONAN_CHANNEL", None),))
    # print("KNUTH_FULL_BUILD:    %s" % (os.getenv("KNUTH_FULL_BUILD", None),))
    # print("KNUTH_CONAN_VERSION: %s" % (os.getenv("KNUTH_CONAN_VERSION", None),))

    version = get_version_from_file()

    # print('------------------------------------------------------')
    # print("version 1: %s" % (version,))

    if version is None:
        version = os.getenv("KNUTH_CONAN_VERSION", None)

    # print("version 2: %s" % (version,))
    # print("KNUTH_CONAN_VERSION: %s" % (os.getenv("KNUTH_CONAN_VERSION", None),))

    if version is None:
        version = get_version_from_branch_name()

    # print("version 3: %s" % (version,))

    if version is None:
        version = get_version_from_git_describe_no_releases(None, is_development_branch())

    # print("version 4: %s" % (version,))
    # print('------------------------------------------------------')

    if version is None:
        version = default


    return version


# def get_version_clean():
#     version = get_version_from_file()

#     if version is None:
#         version = os.getenv("KNUTH_CONAN_VERSION", None)

#     if version is None:
#         version = get_version_from_branch_name_clean()

#     if version is None:
#         version = get_version_from_git_describe_clean(None, is_development_branch_clean())

#     return version


def get_channel_from_file():
    return get_content_default('conan_channel')


def branch_to_channel(branch):
    if branch is None:
        return "staging"
    if branch == 'dev':
        return "testing"
    if branch.startswith('release'):
        return "staging"
    if branch.startswith('hotfix'):
        return "staging"
    if branch.startswith('feature'):
        return branch

    return "staging"

def get_channel_from_branch():
    return branch_to_channel(get_branch())
    
def get_channel():
    channel = get_channel_from_file()

    if channel is None:
        channel = os.getenv("KNUTH_CONAN_CHANNEL", None)

    if channel is None:
        # channel = get_git_branch()
        channel = get_channel_from_branch()

    if channel is None:
        channel = 'staging'

    return channel

def get_user():
    # return get_content('conan_user')
    return get_content_default('conan_user', DEFAULT_USERNAME)

def get_repository():
    return os.getenv("BIPRIM_BINTRAY_REPOSITORY", DEFAULT_REPOSITORY)

def get_conan_req_version():
    return get_content('conan_req_version')

def get_conan_vars():
    org_name = os.getenv("CONAN_ORGANIZATION_NAME", DEFAULT_ORGANIZATION_NAME)
    login_username = os.getenv("CONAN_LOGIN_USERNAME", DEFAULT_LOGIN_USERNAME)
    username = os.getenv("CONAN_USERNAME", get_user())
    channel = os.getenv("CONAN_CHANNEL", get_channel())
    version = os.getenv("CONAN_VERSION", get_version())
    return org_name, login_username, username, channel, version

def get_value_from_recipe(search_string, recipe_name="conanfile.py"):
    recipe_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', recipe_name)
    with open(recipe_path, "r") as conanfile:
        contents = conanfile.read()
        result = re.search(search_string, contents)
    return result

def get_name_from_recipe():
    return get_value_from_recipe(r'''name\s*=\s*["'](\S*)["']''').groups()[0]

def get_user_repository(org_name, repository_name):
    # https://api.bintray.com/conan/k-nuth/kth
    return "https://api.bintray.com/conan/{0}/{1}".format(org_name.lower(), repository_name)

def get_conan_upload(org_name):
    repository_name = get_repository()
    return os.getenv("CONAN_UPLOAD", get_user_repository(org_name, repository_name))

def get_conan_upload_for_remote(org_name):
    repository_name = get_repository()
    return get_user_repository(org_name, repository_name)

def get_conan_remotes(org_name):
    # While redundant, this moves upload remote to position 0.
    remotes = [get_conan_upload_for_remote(org_name),
              'https://api.bintray.com/conan/bitprim/bitprim']

    # # Add bincrafters repository for other users, e.g. if the package would
    # # require other packages from the bincrafters repo.
    # bincrafters_user = "bincrafters"
    # if username != bincrafters_user:
    #     remotes.append(get_conan_upload(bincrafters_user))
    return remotes

def get_os():
    return platform.system().replace("Darwin", "Macos")

def get_archs():
    return ["x86_64"]
    # archs = os.getenv("CONAN_ARCHS", None)
    # if get_os() == "Macos" and archs is None:
    #     return ["x86_64"]
    # return split_colon_env("CONAN_ARCHS") if archs else None


def get_builder(args=None):
    name = get_name_from_recipe()
    org_name, login_username, username, channel, version = get_conan_vars()
    reference = "{0}/{1}".format(name, version)
    upload = get_conan_upload(org_name)
    remotes = os.getenv("CONAN_REMOTES", get_conan_remotes(org_name))

    # upload_when_stable = get_upload_when_stable()
    # stable_branch_pattern = os.getenv("CONAN_STABLE_BRANCH_PATTERN", "stable/*")

    archs = get_archs()

    # print((login_username, username, channel, version, archs))


    builder = get_conan_packager().ConanMultiPackager(
        # args=args,    # Removed on https://github.com/conan-io/conan-package-tools/pull/269
        username=username,
        login_username=login_username,
        channel=channel,
        reference=reference,
        upload=upload,
        remotes=remotes,
        archs=archs,
        # upload_only_when_stable=upload_when_stable,
        # stable_branch_pattern=stable_branch_pattern
        )

    return builder, name

def handle_microarchs(opt_name, microarchs, filtered_builds, settings, options, env_vars, build_requires):
    microarchs = list(set(microarchs))

    for ma in microarchs:
        opts_copy = copy.deepcopy(options)
        opts_copy[opt_name] = ma
        filtered_builds.append([settings, opts_copy, env_vars, build_requires])

def filter_marchs_tests(name, builds, test_options, march_opt=None):
    if march_opt is None:
        march_opt = "%s:microarchitecture" % name

    for b in builds:
        options = b[1]
        if options[march_opt] != "x86-64":
            for to in test_options:
                options[to] = "False"



# --------------------------------------------

# https://gcc.gnu.org/onlinedocs/gcc-4.8.0/gcc/i386-and-x86_002d64-Options.html
# https://gcc.gnu.org/onlinedocs/gcc-7.4.0/gcc/x86-Options.html#x86-Options
# https://gcc.gnu.org/onlinedocs/gcc-8.3.0/gcc/x86-Options.html#x86-Options
# https://gcc.gnu.org/onlinedocs/gcc-9.1.0/gcc/x86-Options.html#x86-Options


microarchitecture_default = 'x86_64'

def get_cpuid():
    try:
        # print("*** cpuid OK")
        cpuid = importlib.import_module('cpuid')
        return cpuid
    except ImportError:
        # print("*** cpuid could not be imported")
        return None

def get_cpu_microarchitecture_or_default(default):
    cpuid = get_cpuid()
    if cpuid != None:
        # return '%s%s' % cpuid.cpu_microarchitecture()
        return '%s' % (''.join(cpuid.cpu_microarchitecture()))
    else:
        return default

def get_cpu_microarchitecture():
    return get_cpu_microarchitecture_or_default(microarchitecture_default)





marchs_extensions = {
    'x86-64':         ['64-bit extensions'],

# Intel Core
    #tock
    'core2':          ['64-bit extensions', 'MMX', 'SSE', 'SSE2', 'SSE3', 'SSSE3'],
    #tick
    # 'penryn':         ['64-bit extensions', 'MMX', 'SSE', 'SSE2', 'SSE3', 'SSSE3', 'SSE4', 'SSE4.1'],
    #tock
    'nehalem':        ['64-bit extensions', 'MMX', 'SSE', 'SSE2', 'SSE3', 'SSSE3', 'SSE4', 'SSE4.1', 'SSE4.2', 'POPCNT'],
    #tick
    'westmere':       ['64-bit extensions', 'MMX', 'SSE', 'SSE2', 'SSE3', 'SSSE3', 'SSE4', 'SSE4.1', 'SSE4.2', 'POPCNT', 'AES', 'PCLMUL'],
    #tock
    'sandybridge':    ['64-bit extensions', 'MMX', 'SSE', 'SSE2', 'SSE3', 'SSSE3', 'SSE4', 'SSE4.1', 'SSE4.2', 'POPCNT', 'AES', 'PCLMUL', 'AVX'],
    #tick
    'ivybridge':      ['64-bit extensions', 'MMX', 'SSE', 'SSE2', 'SSE3', 'SSSE3', 'SSE4', 'SSE4.1', 'SSE4.2', 'POPCNT', 'AES', 'PCLMUL', 'AVX', 'FSGSBASE', 'RDRND', 'F16C'],
    #tock
    'haswell':        ['64-bit extensions', 'MMX', 'SSE', 'SSE2', 'SSE3', 'SSSE3', 'SSE4', 'SSE4.1', 'SSE4.2', 'POPCNT', 'AES', 'PCLMUL', 'AVX', 'FSGSBASE', 'RDRND', 'F16C', 'FMA', 'BMI', 'BMI2', 'MOVBE', 'AVX2'],
    #tick/process
    'broadwell':      ['64-bit extensions', 'MMX', 'SSE', 'SSE2', 'SSE3', 'SSSE3', 'SSE4', 'SSE4.1', 'SSE4.2', 'POPCNT', 'AES', 'PCLMUL', 'AVX', 'FSGSBASE', 'RDRND', 'F16C', 'FMA', 'BMI', 'BMI2', 'MOVBE', 'AVX2', 'RDSEED', 'ADCX', 'PREFETCHW'],  #TXT, TSX, 
                                 

    'skylake':        ['64-bit extensions', 'MMX', 'SSE', 'SSE2', 'SSE3', 'SSSE3', 'SSE4', 'SSE4.1', 'SSE4.2', 'POPCNT', 'AES', 'PCLMUL', 'AVX', 'FSGSBASE', 'RDRND', 'F16C', 'FMA', 'BMI', 'BMI2', 'MOVBE', 'AVX2', 'RDSEED', 'ADCX', 'PREFETCHW', 'CLFLUSHOPT', 'XSAVEC', 'XSAVES'],
    'skylake-avx512': ['64-bit extensions', 'MMX', 'SSE', 'SSE2', 'SSE3', 'SSSE3', 'SSE4', 'SSE4.1', 'SSE4.2', 'POPCNT', 'AES', 'PCLMUL', 'AVX', 'FSGSBASE', 'RDRND', 'F16C', 'FMA', 'BMI', 'BMI2', 'MOVBE', 'AVX2', 'RDSEED', 'ADCX', 'PREFETCHW', 'CLFLUSHOPT', 'XSAVEC', 'XSAVES', 'AVX512F', 'AVX512CD', 'AVX512VL', 'AVX512BW', 'AVX512DQ', 'PKU', 'CLWB'],
    # Kaby Lake
    # Coffee Lake
    # Whiskey Lake
    # Cascade Lake
    'cascadelake':    ['64-bit extensions', 'MMX', 'SSE', 'SSE2', 'SSE3', 'SSSE3', 'SSE4', 'SSE4.1', 'SSE4.2', 'POPCNT', 'AES', 'PCLMUL', 'AVX', 'FSGSBASE', 'RDRND', 'F16C', 'FMA', 'BMI', 'BMI2', 'MOVBE', 'AVX2', 'RDSEED', 'ADCX', 'PREFETCHW', 'CLFLUSHOPT', 'XSAVEC', 'XSAVES', 'AVX512F', 'AVX512CD', 'AVX512VL', 'AVX512BW', 'AVX512DQ', 'PKU', 'CLWB', 'AVX512VNNI'],

    'cannonlake':     ['64-bit extensions', 'MMX', 'SSE', 'SSE2', 'SSE3', 'SSSE3', 'SSE4', 'SSE4.1', 'SSE4.2', 'POPCNT', 'AES', 'PCLMUL', 'AVX', 'FSGSBASE', 'RDRND', 'F16C', 'FMA', 'BMI', 'BMI2', 'MOVBE', 'AVX2', 'RDSEED', 'ADCX', 'PREFETCHW', 'CLFLUSHOPT', 'XSAVEC', 'XSAVES', 'AVX512F', 'AVX512CD', 'AVX512VL', 'AVX512BW', 'AVX512DQ', 'PKU', '????', 'AVX512VBMI', 'AVX512IFMA', 'SHA', 'UMIP'],
    'icelake-client': ['64-bit extensions', 'MMX', 'SSE', 'SSE2', 'SSE3', 'SSSE3', 'SSE4', 'SSE4.1', 'SSE4.2', 'POPCNT', 'AES', 'PCLMUL', 'AVX', 'FSGSBASE', 'RDRND', 'F16C', 'FMA', 'BMI', 'BMI2', 'MOVBE', 'AVX2', 'RDSEED', 'ADCX', 'PREFETCHW', 'CLFLUSHOPT', 'XSAVEC', 'XSAVES', 'AVX512F', 'AVX512CD', 'AVX512VL', 'AVX512BW', 'AVX512DQ', 'PKU', 'CLWB', 'AVX512VBMI', 'AVX512IFMA', 'SHA', 'UMIP', 'RDPID', 'GFNI', 'AVX512VBMI2', 'AVX512VPOPCNTDQ', 'AVX512BITALG', 'AVX512VNNI', 'VPCLMULQDQ', 'VAES'],
    'icelake-server': ['64-bit extensions', 'MMX', 'SSE', 'SSE2', 'SSE3', 'SSSE3', 'SSE4', 'SSE4.1', 'SSE4.2', 'POPCNT', 'AES', 'PCLMUL', 'AVX', 'FSGSBASE', 'RDRND', 'F16C', 'FMA', 'BMI', 'BMI2', 'MOVBE', 'AVX2', 'RDSEED', 'ADCX', 'PREFETCHW', 'CLFLUSHOPT', 'XSAVEC', 'XSAVES', 'AVX512F', 'AVX512CD', 'AVX512VL', 'AVX512BW', 'AVX512DQ', 'PKU', 'CLWB', 'AVX512VBMI', 'AVX512IFMA', 'SHA', 'UMIP', 'RDPID', 'GFNI', 'AVX512VBMI2', 'AVX512VPOPCNTDQ', 'AVX512BITALG', 'AVX512VNNI', 'VPCLMULQDQ', 'VAES', 'PCONFIG', 'WBNOINVD'],
    # Tiger Lake
    # Sapphire Rapids

# Intel Atom
    'bonnell':        ['64-bit extensions', 'MMX', 'SSE', 'SSE2', 'SSE3', 'SSSE3', 'MOVBE'],
    'silvermont':     ['64-bit extensions', 'MMX', 'SSE', 'SSE2', 'SSE3', 'SSSE3', 'MOVBE', 'SSE4', 'SSE4.1', 'SSE4.2', 'POPCNT', 'AES', 'PCLMUL', 'RDRND'],
    'goldmont':       ['64-bit extensions', 'MMX', 'SSE', 'SSE2', 'SSE3', 'SSSE3', 'MOVBE', 'SSE4', 'SSE4.1', 'SSE4.2', 'POPCNT', 'AES', 'PCLMUL', 'RDRND', 'XSAVE', 'XSAVEOPT', 'FSGSBASE'],
    'goldmont-plus':  ['64-bit extensions', 'MMX', 'SSE', 'SSE2', 'SSE3', 'SSSE3', 'MOVBE', 'SSE4', 'SSE4.1', 'SSE4.2', 'POPCNT', 'AES', 'PCLMUL', 'RDRND', 'XSAVE', 'XSAVEOPT', 'FSGSBASE', 'PTWRITE', 'RDPID', 'SGX', 'UMIP'],
    'tremont':        ['64-bit extensions', 'MMX', 'SSE', 'SSE2', 'SSE3', 'SSSE3', 'MOVBE', 'SSE4', 'SSE4.1', 'SSE4.2', 'POPCNT', 'AES', 'PCLMUL', 'RDRND', 'XSAVE', 'XSAVEOPT', 'FSGSBASE', 'PTWRITE', 'RDPID', 'SGX', 'UMIP', 'GFNI-SSE', 'CLWB', 'ENCLV'],

# Intel High-end
    'knl':            ['64-bit extensions', 'MMX', 'SSE', 'SSE2', 'SSE3', 'SSSE3', 'SSE4', 'SSE4.1', 'SSE4.2', 'POPCNT', 'AES', 'PCLMUL', 'AVX', 'FSGSBASE', 'RDRND', 'F16C', 'FMA', 'BMI', 'BMI2', 'MOVBE', 'AVX2', 'RDSEED', 'ADCX', 'PREFETCHW',                                   'AVX512F', 'AVX512CD', 'AVX512PF', 'AVX512ER'],
    'knm':            ['64-bit extensions', 'MMX', 'SSE', 'SSE2', 'SSE3', 'SSSE3', 'SSE4', 'SSE4.1', 'SSE4.2', 'POPCNT', 'AES', 'PCLMUL', 'AVX', 'FSGSBASE', 'RDRND', 'F16C', 'FMA', 'BMI', 'BMI2', 'MOVBE', 'AVX2', 'RDSEED', 'ADCX', 'PREFETCHW',                                   'AVX512F', 'AVX512CD', 'AVX512PF', 'AVX512ER', 'AVX5124VNNIW', 'AVX5124FMAPS', 'AVX512VPOPCNTDQ'],



# AMD       https://en.wikipedia.org/wiki/List_of_AMD_CPU_microarchitectures
#           AMD K8 Hammer: k8, opteron, athlon64, athlon-fx
#           https://en.wikipedia.org/wiki/AMD_K8
    'k8':            ['64-bit extensions', 'MMX', 'SSE', 'SSE2', '3DNow!', 'enhanced 3DNow!'],
    'opteron':       ['64-bit extensions', 'MMX', 'SSE', 'SSE2', '3DNow!', 'enhanced 3DNow!'],
    'athlon64':      ['64-bit extensions', 'MMX', 'SSE', 'SSE2', '3DNow!', 'enhanced 3DNow!'],
    'athlon-fx':     ['64-bit extensions', 'MMX', 'SSE', 'SSE2', '3DNow!', 'enhanced 3DNow!'],

#           AMD K8 Hammer with SSE3: k8-sse3, opteron-sse3, athlon64-sse3
    'k8-sse3':       ['64-bit extensions', 'MMX', 'SSE', 'SSE2', '3DNow!', 'enhanced 3DNow!', 'SSE3'],
    'opteron-sse3':  ['64-bit extensions', 'MMX', 'SSE', 'SSE2', '3DNow!', 'enhanced 3DNow!', 'SSE3'],
    'athlon64-sse3': ['64-bit extensions', 'MMX', 'SSE', 'SSE2', '3DNow!', 'enhanced 3DNow!', 'SSE3'],

#           AMD Family 10h, or K10: amdfam10, barcelona            
#           https://en.wikipedia.org/wiki/AMD_10h
    'amdfam10':      ['64-bit extensions', 'MMX', 'SSE', 'SSE2', '3DNow!', 'enhanced 3DNow!', 'SSE3', 'SSE4A', 'ABM'],
    'barcelona':     ['64-bit extensions', 'MMX', 'SSE', 'SSE2', '3DNow!', 'enhanced 3DNow!', 'SSE3', 'SSE4A', 'ABM'],

#           AMD Bobcat Family 14h (low-power/low-cost market)   https://en.wikipedia.org/wiki/Bobcat_(microarchitecture)
    'btver1':        ['64-bit extensions', 'MMX', 'SSE', 'SSE2', '3DNow!', 'enhanced 3DNow!', 'SSE3', 'SSE4A', 'ABM', 'SSSE3', 'CX16'],
#           AMD Jaguar Family 16h (low-power/low-cost market)   https://en.wikipedia.org/wiki/Jaguar_(microarchitecture)
    'btver2':        ['64-bit extensions', 'MMX', 'SSE', 'SSE2', '3DNow!', 'enhanced 3DNow!', 'SSE3', 'SSE4A', 'ABM', 'SSSE3', 'CX16', 'MOVBE', 'F16C', 'BMI', 'AVX', 'PCL_MUL', 'AES', 'SSE4.2', 'SSE4.1'],
#           AMD Puma Family 16h (2nd-gen) (low-power/low-cost market)   https://en.wikipedia.org/wiki/Puma_(microarchitecture)
#           ????

#           AMD Bulldozer Family 15h (1st-gen)      https://en.wikipedia.org/wiki/Bulldozer_(microarchitecture)
    'bdver1':        ['64-bit extensions', 'MMX', 'SSE', 'SSE2', '3DNow!', 'enhanced 3DNow!', 'SSE3', 'SSE4A', 'ABM', 'SSSE3', 'SSE4.1', 'SSE4.2', 'FMA4', 'AVX', 'XOP', 'LWP', 'AES', 'PCL_MUL', 'CX16'],
#           AMD Piledriver Family 15h (2nd-gen)     https://en.wikipedia.org/wiki/Piledriver_(microarchitecture)
    'bdver2':        ['64-bit extensions', 'MMX', 'SSE', 'SSE2', '3DNow!', 'enhanced 3DNow!', 'SSE3', 'SSE4A', 'ABM', 'SSSE3', 'SSE4.1', 'SSE4.2', 'FMA4', 'AVX', 'XOP', 'LWP', 'AES', 'PCL_MUL', 'CX16', 'BMI', 'TBM', 'F16C', 'FMA'],
#           AMD Steamroller Family 15h (3rd-gen)    https://en.wikipedia.org/wiki/Steamroller_(microarchitecture)
    'bdver3':        ['64-bit extensions', 'MMX', 'SSE', 'SSE2', '3DNow!', 'enhanced 3DNow!', 'SSE3', 'SSE4A', 'ABM', 'SSSE3', 'SSE4.1', 'SSE4.2', 'FMA4', 'AVX', 'XOP', 'LWP', 'AES', 'PCL_MUL', 'CX16', 'BMI', 'TBM', 'F16C', 'FMA', 'FSGSBASE'],
#           AMD Excavator Family 15h (4th-gen)      https://en.wikipedia.org/wiki/Excavator_(microarchitecture)
    'bdver4':        ['64-bit extensions', 'MMX', 'SSE', 'SSE2', '3DNow!', 'enhanced 3DNow!', 'SSE3', 'SSE4A', 'ABM', 'SSSE3', 'SSE4.1', 'SSE4.2', 'FMA4', 'AVX', 'XOP', 'LWP', 'AES', 'PCL_MUL', 'CX16', 'BMI', 'TBM', 'F16C', 'FMA', 'FSGSBASE', 'AVX2', 'BMI2', 'MOVBE'],
#           AMD Zen                                 https://en.wikipedia.org/wiki/Zen_(microarchitecture)
    'znver1':        ['64-bit extensions', 'MMX', 'SSE', 'SSE2', '3DNow!', 'enhanced 3DNow!', 'SSE3', 'SSE4A', 'ABM', 'SSSE3', 'SSE4.1', 'SSE4.2', 'FMA4', 'AVX', 'XOP', 'LWP', 'AES', 'PCL_MUL', 'CX16', 'BMI', 'TBM', 'F16C', 'FMA', 'FSGSBASE', 'AVX2', 'BMI2', 'MOVBE', 'ADCX', 'RDSEED', 'MWAITX', 'SHA', 'CLZERO', 'XSAVEC', 'XSAVES', 'CLFLUSHOPT', 'POPCNT'],
#           AMD Zen 2                               https://en.wikipedia.org/wiki/Zen_2
    'znver2':        ['64-bit extensions', 'MMX', 'SSE', 'SSE2', '3DNow!', 'enhanced 3DNow!', 'SSE3', 'SSE4A', 'ABM', 'SSSE3', 'SSE4.1', 'SSE4.2', 'FMA4', 'AVX', 'XOP', 'LWP', 'AES', 'PCL_MUL', 'CX16', 'BMI', 'TBM', 'F16C', 'FMA', 'FSGSBASE', 'AVX2', 'BMI2', 'MOVBE', 'ADCX', 'RDSEED', 'MWAITX', 'SHA', 'CLZERO', 'XSAVEC', 'XSAVES', 'CLFLUSHOPT', 'POPCNT', 'CLWB'],

# VIA
    'eden-x2':        ['64-bit extensions', 'MMX', 'SSE', 'SSE2', 'SSE3'],
    'eden-x4':        ['64-bit extensions', 'MMX', 'SSE', 'SSE2', 'SSE3', 'SSSE3', 'SSE4.1', 'SSE4.2', 'AVX', 'AVX2'],

    'nano':           ['64-bit extensions', 'MMX', 'SSE', 'SSE2', 'SSE3', 'SSSE3'],
    'nano-1000':      ['64-bit extensions', 'MMX', 'SSE', 'SSE2', 'SSE3', 'SSSE3'], 
    'nano-2000':      ['64-bit extensions', 'MMX', 'SSE', 'SSE2', 'SSE3', 'SSSE3'], 
    'nano-3000':      ['64-bit extensions', 'MMX', 'SSE', 'SSE2', 'SSE3', 'SSSE3', 'SSE4.1'], 
    'nano-x2':        ['64-bit extensions', 'MMX', 'SSE', 'SSE2', 'SSE3', 'SSSE3', 'SSE4.1'], 
    'nano-x4':        ['64-bit extensions', 'MMX', 'SSE', 'SSE2', 'SSE3', 'SSSE3', 'SSE4.1'], 

}


marchs_aliases = {
    'k8':            'k8',
    'opteron':       'k8',
    'athlon64':      'k8',
    'athlon-fx':     'k8',
    'k8-sse3':       'k8-sse3',
    'opteron-sse3':  'k8-sse3',
    'athlon64-sse3': 'k8-sse3',
    'k10':           'amdfam10',
    'amdfam10':      'amdfam10',
    'barcelona':     'amdfam10',
    'bobcat':        'btver1',
    'jaguar':        'btver2',
    # 'puma':          'btver2',
    # 'leopard':       'btver3',
    # 'margay':        'btver4',
    'bulldozer':      'bdver1',
    'piledriver':     'bdver2',
    'steamroller':    'bdver3',
    'excavator':      'bdver4',

    'knightslanding': 'knl',
    'atom':           'bonnell',
    'kabylake':       'skylake',
}

def remove_ext(data, ext):
    for _, value in data.items():
        if ext in value:
            value.remove(ext)


marchs_families = {}
marchs_families['gcc']= {}
marchs_families['apple-clang']= {}
marchs_families['clang']= {}
marchs_families['msvc']= {}
marchs_families['mingw']= {}

# msvc 2019
    # (x86)
        # /arch:[IA32|SSE|SSE2|AVX|AVX2]  
    # (x64)
        # /arch:[AVX|AVX2]  
    # (ARM)
        # /arch:[ARMv7VE|VFPv4]  

# msvc 2017
    # (x86)
        # /arch:[IA32|SSE|SSE2|AVX|AVX2]  
    # (x64)
        # /arch:[AVX|AVX2]  
    # (ARM)
        # /arch:[ARMv7VE|VFPv4]  

marchs_families['msvc'][14] = {
    'amd_high':   ['x86-64', 'bdver1', 'bdver4'],
    'amd_low':    ['x86-64', 'btver2'],
    'intel_core': ['x86-64', 'sandybridge', 'haswell'],
    'via_eden':   ['x86-64', 'eden-x4'],
}

marchs_families['msvc'][15] = copy.deepcopy(marchs_families['msvc'][14])
marchs_families['msvc'][16] = copy.deepcopy(marchs_families['msvc'][15])


msvc_to_extensions = {
    'x86-64':        None,
    'bdver1':       'AVX',
    'bdver4':       'AVX2',
    'btver2':       'AVX',
    'sandybridge':  'AVX',
    'haswell':      'AVX2',
    'eden-x4':      'AVX2',
}

def msvc_to_ext(march):
    march_str = str(march)
    # print(march_str)
    if march_str in msvc_to_extensions:
        return msvc_to_extensions[march_str]
    return None

marchs_families_base = {
    'amd_high':   ['x86-64', 'k8', 'k8-sse3', 'amdfam10', 'bdver1', 'bdver2', 'bdver3', 'bdver4'],
    'amd_low':    ['x86-64', 'k8', 'k8-sse3', 'amdfam10', 'btver1', 'btver2'],
    # 'intel_core': ['x86-64', 'core2', 'penryn', 'nehalem', 'westmere', 'sandybridge', 'ivybridge', 'haswell', 'broadwell'],
    'intel_core': ['x86-64', 'core2', 'nehalem', 'westmere', 'sandybridge', 'ivybridge', 'haswell', 'broadwell'],
    'intel_atom': ['x86-64', 'core2', 'bonnell', 'silvermont'],
}

marchs_families_clang_base = copy.deepcopy(marchs_families_base)
marchs_families_clang_base['intel_high'] = copy.deepcopy(marchs_families_clang_base['intel_core'])
marchs_families_clang_base['intel_core'].extend(['skylake', 'skylake-avx512', 'cannonlake'])
marchs_families_clang_base['intel_high'].extend(['knl'])

marchs_families['clang'][4.0] = copy.deepcopy(marchs_families_clang_base)
marchs_families['clang'][4.0]['amd_high'].extend(['znver1'])

marchs_families['apple-clang'][9.1] = copy.deepcopy(marchs_families['clang'][4.0])
marchs_families['apple-clang'][9.1]['intel_atom'].extend(['goldmont'])

marchs_families['gcc'][4] = copy.deepcopy(marchs_families_base)

marchs_families['gcc'][5] = copy.deepcopy(marchs_families['gcc'][4])
marchs_families['gcc'][5]['intel_high'] = copy.deepcopy(marchs_families['gcc'][5]['intel_core'])
marchs_families['gcc'][5]['intel_high'].extend(['knl'])

marchs_families['mingw'][7] = copy.deepcopy(marchs_families['gcc'][5])
marchs_families['mingw'][7]['intel_core'].extend(['skylake'])
marchs_families['mingw'][7]['amd_high'].extend(['znver1'])

marchs_families['gcc'][6] = copy.deepcopy(marchs_families['mingw'][7])
marchs_families['gcc'][6]['intel_core'].extend(['skylake-avx512'])
marchs_families['gcc'][6]['amd_high'].extend(['znver1'])

marchs_families['mingw'][6] = copy.deepcopy(marchs_families['gcc'][6])
remove_ext(marchs_families['mingw'][6], "skylake-avx512")

marchs_families['mingw'][5] = copy.deepcopy(marchs_families['gcc'][5])

marchs_families['gcc'][7] = copy.deepcopy(marchs_families['gcc'][6])
marchs_families['gcc'][7]['via_eden'] = ['x86-64', 'eden-x2', 'eden-x4']
marchs_families['gcc'][7]['via_nano'] = ['x86-64', 'nano', 'nano-1000', 'nano-2000', 'nano-3000', 'nano-x2', 'nano-x4']

marchs_families['gcc'][8] = copy.deepcopy(marchs_families['gcc'][7])
marchs_families['gcc'][8]['intel_high'].extend(['knm'])
marchs_families['gcc'][8]['intel_core'].extend(['cannonlake', 'icelake-client', 'icelake-server'])

marchs_families['gcc'][9] = copy.deepcopy(marchs_families['gcc'][8])
marchs_families['gcc'][9]['intel_atom'].extend(['goldmont', 'goldmont-plus', 'tremont'])
marchs_families['gcc'][9]['intel_core'].extend(['cascadelake'])



marchs_families['mingw'][8] = copy.deepcopy(marchs_families['gcc'][7])
marchs_families['mingw'][8]['intel_high'].extend(['knm'])
remove_ext(marchs_families['mingw'][8], "skylake-avx512")

#TODO(fernando): Check MinGW9
marchs_families['mingw'][9] = copy.deepcopy(marchs_families['gcc'][8])


# marchs_families['clang'][4.0] = copy.deepcopy(marchs_families['apple-clang'][9.1])
marchs_families['clang'][5.0] = copy.deepcopy(marchs_families['apple-clang'][9.1])
marchs_families['clang'][6.0] = copy.deepcopy(marchs_families['clang'][5.0])
marchs_families['clang'][7.0] = copy.deepcopy(marchs_families['clang'][6.0])

#TODO(fernando): check if new march are supported in apple-clang 10.0
marchs_families['apple-clang'][10.0] = copy.deepcopy(marchs_families['apple-clang'][9.1])
marchs_families['apple-clang'][9.0] = copy.deepcopy(marchs_families['apple-clang'][9.1])
marchs_families['apple-clang'][8.3] = copy.deepcopy(marchs_families_clang_base)
marchs_families['apple-clang'][8.1] = copy.deepcopy(marchs_families_clang_base)
marchs_families['apple-clang'][7.3] = copy.deepcopy(marchs_families_clang_base)
remove_ext(marchs_families['apple-clang'][7.3], "skylake")
remove_ext(marchs_families['apple-clang'][7.3], "cannonlake")
remove_ext(marchs_families['apple-clang'][7.3], "skylake-avx512")


def get_full_family():
    return marchs_families['gcc'][9]

def translate_alias(alias):
    alias_str = str(alias)
    if alias_str in marchs_aliases:
        return marchs_aliases[alias_str]
    else:
        return alias

def adjust_compiler_name(os, compiler):
    if os == "Windows" and compiler == "gcc":
        return "mingw"
    if compiler == "Visual Studio":
        return "msvc"
        
    return compiler
        
def get_march_basis(march_detected, os, compiler, compiler_version, full, default):
    compiler = adjust_compiler_name(os, compiler)

    if compiler not in marchs_families:
        return default

    if compiler_version not in marchs_families[compiler]:
        return default

    data = marchs_families[compiler][compiler_version]
    march_detected = translate_alias(march_detected)

    for key, value in data.items():
        if march_detected in value:
            return march_detected
        else:
            if march_detected in full[key]:
                idx = full[key].index(march_detected)
                idx = min(idx, len(value) - 1)
                return value[idx]

    return default

def get_march(march_detected, os, compiler, compiler_version):
    full = get_full_family()
    default = 'x86-64'
    return get_march_basis(march_detected, os, compiler, compiler_version, full, default)

def march_exists_in(march_detected, os, compiler, compiler_version):
    compiler = adjust_compiler_name(os, compiler)

    if compiler not in marchs_families:
        return False

    if compiler_version not in marchs_families[compiler]:
        return False

    data = marchs_families[compiler][compiler_version]
    march_detected = translate_alias(march_detected)

    for _, value in data.items():
        if march_detected in value:
            return True

    return False

def march_exists_full(march_detected):
    data = get_full_family()
    march_detected = translate_alias(march_detected)

    for _, value in data.items():
        if march_detected in value:
            return True

    return False

def marchs_full_list_basis(data):
    ret = []
    for _, value in data.items():
        ret.extend(value)
    return list(set(ret))

def marchs_full_list():
    full = get_full_family()
    return marchs_full_list_basis(full)

def marchs_compiler_list(os, compiler, compiler_version):
    compiler = adjust_compiler_name(os, compiler)

    if compiler not in marchs_families:
        return []

    if compiler_version not in marchs_families[compiler]:
        return []

    data = marchs_families[compiler][compiler_version]
    return marchs_full_list_basis(data)

def filter_valid_exts(os, compiler, compiler_version, exts):
    data = marchs_compiler_list(os, compiler, compiler_version)

    ret = []
    for x in exts:
        if x in data:
            ret.append(x)

    return list(set(ret))

def march_close_name(march_incorrect): #, compiler, compiler_version):
    # full = get_full_family()
    return difflib.get_close_matches(march_incorrect, marchs_full_list())
    



def march_conan_manip(conanobj):

    # conanobj.output.warn("conanobj.settings.arch '%s'" % conanobj.settings.arch)
    # conanobj.output.warn("conanobj.options.microarchitecture '%s'" % conanobj.options.microarchitecture)
    # conanobj.output.warn("conanobj.settings.os '%s'" % conanobj.settings.os)
    # conanobj.output.warn("conanobj.settings.compiler '%s'" % conanobj.settings.compiler)
    # conanobj.output.warn("conanobj.settings.compiler.version '%s'" % conanobj.settings.compiler.version)

    if conanobj.settings.arch != "x86_64":
        return

    if conanobj.options.microarchitecture == "_DUMMY_":
        conanobj.options.microarchitecture = get_cpu_microarchitecture().replace('_', '-')
        if get_cpuid() == None:
            march_from = 'default'
        else:
            march_from = 'taken from cpuid'
    else:
        march_from = 'user defined'

        # conanobj.output.error("%s" % (marchs_full_list(),))

        if not march_exists_full(conanobj.options.microarchitecture):
            close = march_close_name(str(conanobj.options.microarchitecture))
            if not conanobj.options.fix_march:
                # conanobj.output.error("fixed_march: %s" % (fixed_march,))

                if len(close) > 0:
                    raise Exception ("Microarchitecture '%s' is not recognized. Did you mean '%s'?." % (conanobj.options.microarchitecture, close[0]))
                    # conanobj.output.error("Microarchitecture '%s' is not recognized. Did you mean '%s'?." % (conanobj.options.microarchitecture, close[0]))
                    # sys.exit
                else:
                    raise Exception ("Microarchitecture '%s' is not recognized." % (conanobj.options.microarchitecture,))
                    # conanobj.output.error("Microarchitecture '%s' is not recognized." % (conanobj.options.microarchitecture,))
                    # sys.exit
            else:
                if len(close) > 0:
                    fixed_march = get_march(close[0], str(conanobj.settings.os), str(conanobj.settings.compiler), float(str(conanobj.settings.compiler.version)))
                else:
                    fixed_march = get_march(conanobj.options.microarchitecture, str(conanobj.settings.os), str(conanobj.settings.compiler), float(str(conanobj.settings.compiler.version)))

                conanobj.output.warn("Microarchitecture '%s' is not recognized, but it will be automatically fixed to '%s'." % (conanobj.options.microarchitecture, fixed_march))
                conanobj.options.microarchitecture = fixed_march

        if not march_exists_in(conanobj.options.microarchitecture, str(conanobj.settings.os), str(conanobj.settings.compiler), float(str(conanobj.settings.compiler.version))):
            fixed_march = get_march(conanobj.options.microarchitecture, str(conanobj.settings.os), str(conanobj.settings.compiler), float(str(conanobj.settings.compiler.version)))
            if not conanobj.options.fix_march:
                raise Exception ("Microarchitecture '%s' is not supported by your compiler, you could use '%s'." % (conanobj.options.microarchitecture,fixed_march))
                # conanobj.output.error("Microarchitecture '%s' is not supported by your compiler, you could use '%s'." % (conanobj.options.microarchitecture,fixed_march))
                # sys.exit
            else:
                conanobj.output.warn("Microarchitecture '%s' is not supported by your compiler, but it will be automatically fixed to '%s'." % (conanobj.options.microarchitecture, fixed_march))


    fixed_march = get_march(conanobj.options.microarchitecture, str(conanobj.settings.os), str(conanobj.settings.compiler), float(str(conanobj.settings.compiler.version)))

    if march_from == 'user defined':
        conanobj.output.info("Provided microarchitecture (%s): %s" % (march_from, conanobj.options.microarchitecture))
    else:
        conanobj.output.info("Detected microarchitecture (%s): %s" % (march_from, conanobj.options.microarchitecture))

    if conanobj.options.microarchitecture != fixed_march:
        conanobj.options.microarchitecture = fixed_march
        conanobj.output.info("Corrected microarchitecture for compiler: %s" % (conanobj.options.microarchitecture,))

def pass_march_to_compiler(conanobj, cmake):
    if conanobj.settings.compiler != "Visual Studio":
        gcc_march = str(conanobj.options.microarchitecture)
        cmake.definitions["CONAN_CXX_FLAGS"] = cmake.definitions.get("CONAN_CXX_FLAGS", "") + " -march=" + gcc_march
        cmake.definitions["CONAN_C_FLAGS"] = cmake.definitions.get("CONAN_C_FLAGS", "") + " -march=" + gcc_march
    else:
        ext = msvc_to_ext(str(conanobj.options.microarchitecture))

        if ext is not None:
            cmake.definitions["CONAN_CXX_FLAGS"] = cmake.definitions.get("CONAN_CXX_FLAGS", "") + " /arch:" + ext
            cmake.definitions["CONAN_C_FLAGS"] = cmake.definitions.get("CONAN_C_FLAGS", "") + " /arch:" + ext



def get_conan_get(package, remote=None, default=None):
    try:
        if remote is None:
            params = ["conan", "get", package]
        else:
            params = ["conan", "get", package, "-r", remote]

        res = subprocess.Popen(params, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, _ = res.communicate()
        if output:
            if res.returncode == 0:
                return output.decode("utf-8")
        return default
    except OSError: # as e:
        return default
    except:
        return default

def get_alias_version(package, remote=None, default=None):
    conan_alias = get_conan_get(package, remote, default)
    conan_alias = conan_alias.split('\n')[4:][0]
    return conan_alias[12:].replace('"', '')


def get_recipe_dir():
    recipe_dir = os.path.dirname(os.path.realpath(__file__))
    return os.path.normpath(recipe_dir + os.sep + os.pardir)

def get_conan_requirements_path():
    return os.path.normpath(get_recipe_dir() + os.sep + 'conan_requirements')

def get_requirements_from_file():
    conan_requirements = get_conan_requirements_path()
    if os.path.exists(conan_requirements):
        # print("conan_requirements exists")
        with open(conan_requirements, 'r') as f:
            return [line.rstrip('\n') for line in f]
    # else:
    #     # print("-----------------------------------------------")
    #     # print("conan_requirements DOESNT exists")
    #     # print(os.getcwd())

    #     recipe_dir = get_recipe_dir()
    #     # print(recipe_dir)
    #     # print(get_conan_requirements_path())

    #     # files = [f for f in os.listdir('.') if os.path.isfile(f)]
    #     files = [f for f in recipe_dir if os.path.isfile(f)]
    #     for f in files:
    #         print(f)

    return []


class KnuthCxx11ABIFixer(ConanFile):
    def configure(self):
        self.output.info("configure() - glibcxx_supports_cxx11_abi: %s" % (self.options.get_safe("glibcxx_supports_cxx11_abi"),))

        if self.options.get_safe("glibcxx_supports_cxx11_abi") is None:
            return

        if not (self.settings.compiler == "gcc" or self.settings.compiler == "clang"):
            self.output.info("glibcxx_supports_cxx11_abi option is only valid for 'gcc' or 'clang' compilers, deleting it. Your compiler is: '%s'." % (str(self.settings.compiler),))
            del self.options.glibcxx_supports_cxx11_abi
            return

        if self.settings.compiler == "gcc" and self.settings.os == "Windows":
            self.output.info("glibcxx_supports_cxx11_abi option is not valid for 'MinGW' compiler, deleting it. Your compiler is: '%s, %s'." % (str(self.settings.compiler),str(self.settings.os)))
            del self.options.glibcxx_supports_cxx11_abi
            return

        if self.settings.get_safe("compiler.libcxx") is None:
            self.output.info("glibcxx_supports_cxx11_abi option is only useful for 'libstdc++' or 'libstdc++11', deleting it. Your compiler.libcxx is: '%s'." % (str(self.settings.compiler.libcxx),))
            del self.options.glibcxx_supports_cxx11_abi
            return

        if not (str(self.settings.compiler.libcxx) == "libstdc++" or str(self.settings.compiler.libcxx) == "libstdc++11"):
            self.output.info("glibcxx_supports_cxx11_abi option is only useful for 'libstdc++' or 'libstdc++11', deleting it. Your compiler.libcxx is: '%s'." % (str(self.settings.compiler.libcxx),))
            del self.options.glibcxx_supports_cxx11_abi
            return

        if self.options.get_safe("glibcxx_supports_cxx11_abi") != "_DUMMY_":
            return

        abi_support = glibcxx_supports_cxx11_abi()
        self.output.info("glibcxx_supports_cxx11_abi(): %s" % (abi_support,))
        
        self.options.glibcxx_supports_cxx11_abi = abi_support
        self.options["*"].glibcxx_supports_cxx11_abi = self.options.glibcxx_supports_cxx11_abi
        self.output.info("configure() - 2 - glibcxx_supports_cxx11_abi: %s" % (self.options.get_safe("glibcxx_supports_cxx11_abi"),))
        self.libcxx_changed = True

        # libcxx_old = str(self.settings.compiler.libcxx)
        # if str(self.settings.compiler.libcxx) == "libstdc++" and abi_support:
        #     self.settings.compiler.libcxx = "libstdc++11"
        #     # self.settings["*"].compiler.libcxx = self.settings.compiler.libcxx
        #     self.output.info("compiler.libcxx changed from %s to %s" % (libcxx_old, str(self.settings.compiler.libcxx),))

        # if str(self.settings.compiler.libcxx) == "libstdc++11" and not abi_support:
        #     self.settings.compiler.libcxx = "libstdc++"
        #     # self.settings["*"].compiler.libcxx = self.settings.compiler.libcxx
        #     self.output.info("compiler.libcxx changed from %s to %s" % (libcxx_old, str(self.settings.compiler.libcxx),))


    def package_id(self):
        self.output.info("package_id() - glibcxx_supports_cxx11_abi: %s" % (self.options.get_safe("glibcxx_supports_cxx11_abi"),))
        # self.info.settings.compiler.libcxx = "libstdc++11"

        #For Knuth Packages libstdc++ and libstdc++11 are the same
        if self.settings.compiler == "gcc" or self.settings.compiler == "clang":
            if self.settings.get_safe("compiler.libcxx") is not None:
                if str(self.settings.compiler.libcxx) == "libstdc++" or str(self.settings.compiler.libcxx) == "libstdc++11":
                    # self.info.settings.compiler.libcxx = "ANY"
                    self.info.settings.compiler.libcxx = "libstdc++"



class KnuthConanFile(KnuthCxx11ABIFixer):
    if Version(conan_version) < Version(get_conan_req_version()):
        raise Exception ("Conan version should be greater or equal than %s. Detected: %s." % (get_conan_req_version(), conan_version))

    def add_reqs(self, reqs):
        for r in reqs:
            self.requires(r % (self.user, self.channel))

    def knuth_requires(self, default_reqs):
        file_reqs = get_requirements_from_file()
        # print(file_reqs)

        if len(file_reqs) != 0:
            self.add_reqs(file_reqs)
        else:
            self.add_reqs(default_reqs)

    @property
    def msvc_mt_build(self):
        # return "MT" in str(self.settings.compiler.runtime)
        return "MT" in str(self.settings.get_safe("compiler.runtime"))

        

    @property
    def fPIC_enabled(self):
        if self.settings.compiler == "Visual Studio":
            return False
        else:
            return self.options.fPIC

    # Version Node-Cint
    # @property
    # def is_shared(self):
    #     # if self.settings.compiler == "Visual Studio" and self.msvc_mt_build:
    #     #     return False
    #     # else:
    #     #     return self.options.shared
    #     return self.options.shared

    @property
    def is_shared(self):
        if self.options.shared and self.msvc_mt_build:
            return False
        else:
            return self.options.shared



    # @property
    # def channel(self):
    #     if not self._channel:
    #         if not self._channel:
    #             self._channel = get_channel()
    #         if not self._channel:
    #             raise ConanException("CONAN_CHANNEL environment variable not defined, "
    #                                  "but self.channel is used in conanfile")
    #     return self._channel

    # @property
    # def user(self):
    #     if not self._user:
    #         self._user = os.getenv("CONAN_USERNAME")
    #         if not self._user:
    #             self._user = get_user()
    #         if not self._user:
    #             raise ConanException("CONAN_USERNAME environment variable not defined, "
    #                                  "but self.user is used in conanfile")
    #     return self._user

    @property
    def channel(self):
        try:
            return super(KnuthConanFile, self).channel
        except ConanException:
            return get_channel()

    @property
    def user(self):
        try:
            return super(KnuthConanFile, self).user
        except ConanException:
            return get_user()



# marchs = filter_valid_exts('Windows', 'Visual Studio', 15, ['x86-64', 'sandybridge', 'ivybridge', 'haswell', 'skylake', 'skylake-avx512'])
# print(marchs)


# >>> difflib.get_close_matches('anlmal', ['car', 'animal', 'house', 'animation'])

# --------------------------------------------------------------------------------

# def print_extensions():
#     ma = get_cpu_microarchitecture()
#     print(ma)
#     print(marchs_extensions[ma])

# print_extensions()
# print( get_march('broadwell', 'gcc', 4) )
# print( get_march('skylake', 'gcc', 4) )
# print( get_march('skylake-avx512', 'gcc', 4) )

# print( get_march('broadwell', 'gcc', 5) )
# print( get_march('skylake', 'gcc', 5) )
# print( get_march('skylake-avx512', 'gcc', 5) )

# print( get_march('broadwell', 'gcc', 6) )
# print( get_march('skylake', 'gcc', 6) )
# print( get_march('skylake-avx512', 'gcc', 6) )

# print( get_march('broadwell', 'gcc', 7) )
# print( get_march('skylake', 'gcc', 7) )
# print( get_march('skylake-avx512', 'gcc', 7) )

# print( get_march('broadwell', 'gcc', 8) )
# print( get_march('skylake', 'gcc', 8) )
# print( get_march('skylake-avx512', 'gcc', 8) )

# print( get_march('knightslanding', 'gcc', 8) )
# print( get_march('excavator', 'gcc', 8) )
# print( get_march('bdver4', 'gcc', 8) )



# --------------------------------------------------------------------------------

# marchs_families_apple91_temp = {
#     'amd_high':   ['x86-64', 'k8', 'k8-sse3', 'amdfam10', 'bdver1', 'bdver2', 'bdver3', 'bdver4', 'znver1'],
#     'amd_low':    ['x86-64', 'k8', 'k8-sse3', 'amdfam10', 'btver1', 'btver2'],

#     'intel_core': ['x86-64', 'core2', 'nehalem', 'westmere', 'sandybridge', 'ivybridge', 'haswell', 'broadwell', 'skylake', 'skylake-avx512', 'cannonlake'],
#     'intel_atom': ['x86-64', 'core2', 'bonnell', 'silvermont', 'goldmont'],
#     'intel_high': ['x86-64', 'core2', 'nehalem', 'westmere', 'sandybridge', 'ivybridge', 'haswell', 'broadwell', 'knl'],
# }

# marchs_families_gcc4_temp = {
#     'amd_high':   ['x86-64', 'k8', 'k8-sse3', 'amdfam10', 'bdver1', 'bdver2', 'bdver3', 'bdver4'],
#     'amd_low':    ['x86-64', 'k8', 'k8-sse3', 'amdfam10', 'btver1', 'btver2'],

#     'intel_core': ['x86-64', 'core2', 'nehalem', 'westmere', 'sandybridge', 'ivybridge', 'haswell', 'broadwell'],
#     'intel_atom': ['x86-64', 'core2', 'bonnell', 'silvermont'],
#     # 'intel_high': ['x86-64', 'core2', 'nehalem', 'westmere', 'sandybridge', 'ivybridge', 'haswell', 'broadwell'],
# }


# marchs_families_gcc8_temp = {
#     'amd_high':   ['x86-64', 'k8', 'k8-sse3', 'amdfam10', 'bdver1', 'bdver2', 'bdver3', 'bdver4', 'znver1'],
#     'amd_low':    ['x86-64', 'k8', 'k8-sse3', 'amdfam10', 'btver1', 'btver2'],

#     'intel_core': ['x86-64', 'core2', 'nehalem', 'westmere', 'sandybridge', 'ivybridge', 'haswell', 'broadwell', 'skylake', 'skylake-avx512', 'cannonlake', 'icelake-client', 'icelake-server'],
#     'intel_atom': ['x86-64', 'core2', 'bonnell', 'silvermont'],
#     'intel_high': ['x86-64', 'core2', 'nehalem', 'westmere', 'sandybridge', 'ivybridge', 'haswell', 'broadwell', 'knl', 'knm'],

#     'via_eden':   ['x86-64', 'eden-x2', 'eden-x4'],
#     'via_nano':   ['x86-64', 'nano', 'nano-1000', 'nano-2000', 'nano-3000', 'nano-x2', 'nano-x4'],
# }


# print(marchs_families['gcc'][4])
# print()
# print(marchs_families['gcc'][5])
# print()
# print(marchs_families['gcc'][6])
# print()
# print(marchs_families['gcc'][7])
# print()
# print(marchs_families['gcc'][8])

# print(marchs_families['gcc'][4] == marchs_families_gcc4_temp)
# print(marchs_families['gcc'][8] == marchs_families_gcc8_temp)
# print(marchs_families['apple-clang'][9.1] == marchs_families_apple91_temp)


# --------------------------------------------------------------------------------


# GCC7 no tiene: knm, cannonlake, icelake-client, icelake-server
# GCC6 no tiene: ninguno de los VIA que tenemos
# GCC5 no tiene: skylake, skylake-avx512, znver1
# GCC4 no tiene: knl

# Apple LLVM version 9.1.0 (clang-902.0.39.1)
    # icelake-client
    # icelake-server
    # goldmont-plus
    # tremont
    # knm
    # eden-x2
    # eden-x4
    # nano
    # nano-1000
    # nano-2000
    # nano-3000
    # nano-x2
    # nano-x4



# https://gcc.gnu.org/onlinedocs/

    # https://gcc.gnu.org/onlinedocs/gcc/x86-Options.html
    # echo "" | gcc -fsyntax-only -march=pepe -xc -
    # nocona core2 nehalem corei7 westmere sandybridge corei7-avx ivybridge core-avx-i haswell core-avx2 broadwell skylake skylake-avx512 bonnell atom silvermont slm knl x86-64 eden-x2 nano nano-1000 nano-2000 nano-3000 nano-x2 eden-x4 nano-x4 k8 k8-sse3 opteron opteron-sse3 athlon64 athlon64-sse3 athlon-fx amdfam10 barcelona bdver1 bdver2 bdver3 bdver4 znver1 btver1 btver2


# g++ --version
# g++ (Ubuntu 7.3.0-16ubuntu3~16.04.1) 7.3.0
# Copyright (C) 2017 Free Software Foundation, Inc.
# This is free software; see the source for copying conditions.  There is NO
# warranty; not even for MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
 
# echo "" | gcc -fsyntax-only -march=pepe -xc -
# cc1: note: valid arguments to '-march=' switch are: nocona core2 nehalem corei7 westmere sandybridge corei7-avx ivybridge core-avx-i haswell core-avx2 broadwell skylake skylake-avx512 bonnell atom silvermont slm knl x86-64 eden-x2 nano nano-1000 nano-2000 nano-3000 nano-x2 eden-x4 nano-x4 k8 k8-sse3 opteron opteron-sse3 athlon64 athlon64-sse3 athlon-fx amdfam10 barcelona bdver1 bdver2 bdver3 bdver4 znver1 btver1 btver2


# echo "" | clang -fsyntax-only -march=x86-64 -xc -




# clang --version
# Apple LLVM version 9.1.0 (clang-902.0.39.1)
# Target: x86_64-apple-darwin17.6.0
# Thread model: posix
# InstalledDir: /Applications/Xcode.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr/bin



# Kaby Lake
#     Successor	
#         Desktop: Coffee Lake (2nd Optimization)
#                  Whiskey Lake (3rd Optimization)
#         Mobile:  Cannon Lake (Process)
#         Servers and Desktop: Cascade Lake (3rd Optimization)[4][5]

# Coffee Lake
#     Successor	
#         Desktop:    Whiskey Lake (3rd Optimization)
#         Mobile:     Cannon Lake (Process)
#         Ice Lake (Architecture)

# Whiskey Lake
#     Successor
# 	    Cannon Lake (Process)
#         Ice Lake (Architecture)

# Cannon Lake (Skymont)
#     Successor
#         Ice Lake (Architecture)

# Cascade Lake
#     Successor
#         Ice Lake (Architecture)

# Ice Lake
#     Successor
#     	Tiger Lake (Optimization)

# Tiger Lake
#     Successor	
#         Sapphire Rapids (unknown)

# Sapphire Rapids
#     Successor	

# Linea Knights
#     Polaris | Larrabee (LRB) | Rock Creek
#     Knights Ferry (KNF) 
#     Knights Corner (KNC) 
#     Knights Landing (KNL) | Knights Mill (KNM)
#     Knights Hill (KNH)
#     Knights Peak (KNP)

# Linea Atom
#     Bonnell         x86-64, MOVBE, MMX, SSE, SSE2, SSE3, SSSE3
#     Saltwell        x86-64, MOVBE, MMX, SSE, SSE2, SSE3, SSSE3
#     Silvermont      x86-64, MOVBE, MMX, SSE, SSE2, SSE3, SSSE3, SSE4.1, SSE4.2, POPCNT, AES, PCLMUL, RDRND
#     Airmont         x86-64, MOVBE, MMX, SSE, SSE2, SSE3, SSSE3, SSE4.1, SSE4.2, POPCNT, AES, PCLMUL, RDRND
#     Goldmont        x86-64, MOVBE, MMX, SSE, SSE2, SSE3, SSSE3, SSE4.1, SSE4.2, POPCNT, AES, PCLMUL, RDRND, SHA
#     Goldmont Plus   x86-64, MOVBE, MMX, SSE, SSE2, SSE3, SSSE3, SSE4.1, SSE4.2, POPCNT, AES, PCLMUL, RDRND, SHA
#     Tremont         x86-64, MOVBE, MMX, SSE, SSE2, SSE3, SSSE3, SSE4.1, SSE4.2, POPCNT, AES, PCLMUL, RDRND, SHA
