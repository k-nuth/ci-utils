from conan.packager import ConanMultiPackager
import os
import copy
import re
import platform
import importlib
import subprocess
import sys

def get_git_branch(default=None):
    try:
        res = subprocess.Popen(["git", "rev-parse", "--abbrev-ref", "HEAD"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, _ = res.communicate()
        if output:
            if res.returncode == 0:
                return output.decode("utf-8").replace('\n', '').replace('\r', '')
        return default
    except OSError: # as e:
        return default
    except:
        return default

def get_git_describe(default=None):
    try:
        res = subprocess.Popen(["git", "describe"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
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

def get_version_from_git_describe(default=None, increment_minor=False):
    describe = get_git_describe()
    
    print('describe')
    print(describe)

    if describe is None:
        return None
    version = describe.split('-')[0][1:]

    if increment_minor:
        version_arr = version.split('.')
        if len(version_arr) != 3:
            # print('version has to be of the following format: xx.xx.xx')
            return None

        version = "%s.%s.%s" % (version_arr[0], str(int(version_arr[1]) + 1), version_arr[2])

    return version


def get_version_from_git_describe_clean(default=None, increment_minor=False):
    describe = get_git_describe()
    
    if describe is None:
        return None
    version = describe.split('-')[0][1:]

    if increment_minor:
        version_arr = version.split('.')
        if len(version_arr) != 3:
            # print('version has to be of the following format: xx.xx.xx')
            return None

        version = "%s.%s.%s" % (version_arr[0], str(int(version_arr[1]) + 1), version_arr[2])

    return version


def copy_env_vars(env_vars):
    env_vars["BITPRIM_BUILD_NUMBER"] = os.getenv('BITPRIM_BUILD_NUMBER', '-')
    env_vars["BITPRIM_BRANCH"] = os.getenv('BITPRIM_BRANCH', '-')
    env_vars["BITPRIM_CONAN_CHANNEL"] = os.getenv('BITPRIM_CONAN_CHANNEL', '-')
    env_vars["BITPRIM_FULL_BUILD"] = os.getenv('BITPRIM_FULL_BUILD', '-')


def is_development_branch():
    branch = get_branch()
    if branch is None: 
        return False

    return branch == 'dev' or branch.startswith('feature')    

def is_development_branch_clean():
    branch = get_branch_clean()
    if branch is None: 
        return False

    return branch == 'dev' or branch.startswith('feature')    


def get_branch():
    branch = os.getenv("BITPRIM_BRANCH", None)
    
    print("branch: %s" % (branch,))

    if branch is None: 
        branch = get_git_branch()

    print("branch: %s" % (branch,))

    return branch

def get_branch_clean():
    branch = os.getenv("BITPRIM_BRANCH", None)
    if branch is None: 
        branch = get_git_branch()
    return branch

def get_version_from_branch_name():
    branch = get_branch()

    if branch is None: 
        return None

    if branch.startswith("release-") or branch.startswith("hotfix-"):
        return branch.split('-', 1)[1]

    if branch.startswith("release_") or branch.startswith("hotfix_"):
        return branch.split('_', 1)[1]

    return None

def get_version_from_branch_name_clean():
    branch = get_branch_clean()

    if branch is None: 
        return None

    if branch.startswith("release-") or branch.startswith("hotfix-"):
        return branch.split('-', 1)[1]

    if branch.startswith("release_") or branch.startswith("hotfix_"):
        return branch.split('_', 1)[1]

    return None


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
    version = get_version_from_file()

    print('------------------------------------------------------')
    print(version)

    if version is None:
        version = os.getenv("BITPRIM_CONAN_VERSION", None)

    print(version)

    if version is None:
        version = get_version_from_branch_name()

    print(version)

    if version is None:
        version = get_version_from_git_describe(None, is_development_branch())

    print(version)
    print('------------------------------------------------------')

    return version

def get_version_clean():
    version = get_version_from_file()

    if version is None:
        version = os.getenv("BITPRIM_CONAN_VERSION", None)

    if version is None:
        version = get_version_from_branch_name_clean()

    if version is None:
        version = get_version_from_git_describe_clean(None, is_development_branch_clean())

    return version


def get_channel_from_file():
    return get_content_default('conan_channel')

def get_channel():
    channel = get_channel_from_file()

    if channel is None:
        channel = os.getenv("BITPRIM_CONAN_CHANNEL", None)

    if channel is None:
        channel = get_git_branch()

    if channel is None:
        channel = 'stable'

    return channel

def get_user():
    # return get_content('conan_user')
    return get_content_default('conan_user', 'bitprim')

def get_conan_req_version():
    return get_content('conan_req_version')

def get_conan_vars():
    login_username = os.getenv("CONAN_LOGIN_USERNAME", "bitprim-bintray")
    username = os.getenv("CONAN_USERNAME", get_user())
    channel = os.getenv("CONAN_CHANNEL", get_channel())
    version = os.getenv("CONAN_VERSION", get_version())
    return login_username, username, channel, version

def get_value_from_recipe(search_string, recipe_name="conanfile.py"):
    recipe_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', recipe_name)
    with open(recipe_path, "r") as conanfile:
        contents = conanfile.read()
        result = re.search(search_string, contents)
    return result

def get_name_from_recipe():
    return get_value_from_recipe(r'''name\s*=\s*["'](\S*)["']''').groups()[0]

def get_user_repository(username, repository_name):
    # https://api.bintray.com/conan/bitprim/bitprim
    return "https://api.bintray.com/conan/{0}/{1}".format(username.lower(), repository_name)

def get_conan_upload(username):
    repository_name = os.getenv("BIPRIM_BINTRAY_REPOSITORY", "bitprim")
    return os.getenv("CONAN_UPLOAD", get_user_repository(username, repository_name))

def get_conan_upload_for_remote(username):
    repository_name = os.getenv("BIPRIM_BINTRAY_REPOSITORY", "bitprim")
    return get_user_repository(username, repository_name)

def get_conan_remotes(username):
    # While redundant, this moves upload remote to position 0.
    remotes = [get_conan_upload_for_remote(username)]

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
    login_username, username, channel, version = get_conan_vars()
    reference = "{0}/{1}".format(name, version)
    upload = get_conan_upload(username)
    remotes = os.getenv("CONAN_REMOTES", get_conan_remotes(username))

    # upload_when_stable = get_upload_when_stable()
    # stable_branch_pattern = os.getenv("CONAN_STABLE_BRANCH_PATTERN", "stable/*")

    archs = get_archs()
    builder = ConanMultiPackager(
        args=args,
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

