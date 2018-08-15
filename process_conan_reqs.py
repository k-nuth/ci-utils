import os
import subprocess

def get_conan_info(default=None):
    try:
        # conan info . --only None  
        params = ["conan", "info", ".", "--only", "None"]
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

def get_conan_requires():
    info = get_conan_info()
    after_proj = False

    res = []
    for line in info.splitlines():
        if not after_proj:
            if line == "PROJECT":
                after_proj = True
        else:
            pos = line.find('/')
            name = line[:pos]
            if name == "secp256k1" or name.startswith("bitprim-"):
                # print(name)
                res.append(name)
    return res



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
    
def write_req_file():
    reqs = get_conan_requires()
    if len(reqs) == 0:
        print("hello")
        return

    if not os.path.exists('conan_requirements'):
        with open("conan_requirements", "w") as file:
            for r in reqs:
                # print(r)
                alias = get_alias_version("%s/0.X@%s/%s" % (r, "bitprim", "stable"), "bitprim")
                pos = alias.find('@')
                alias = alias[:pos]
                alias = alias + "@%s/%s"
                # print(alias)
                file.write(alias)


channel = os.environ.get('BITPRIM_CONAN_CHANNEL')
print("--------------------------------------------")
print("process_conan_reqs.py")
print(channel)
print("--------------------------------------------")

if channel == 'staging':
    write_req_file()
