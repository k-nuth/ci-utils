import os
import pipes
import platform
from utils import get_version
import sys
import time
import subprocess

remote = "kthbuild_kth_temp_"


def get_conan_search(package, remote):
    try:
        # conan search infrastructure/0.X@kth/staging -r kth_temp > $null
        params = ["conan", "search", package, "-r", remote]
        command = " ".join(params)
        # print("executing for %s ..." % (command,))
        res = subprocess.Popen(params, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, _ = res.communicate()
        if output:
            return res.returncode
        return 1
    except OSError: # as e:
        return 1
    except Error as e:
        return 1

deps_graph = {
    "secp256k1": [],
    "infrastructure": ["secp256k1"],
    "domain": ["infrastructure"],
    "consensus": ["secp256k1", "domain"],
    "database":["domain"],
    "network":["domain"],
    "blockchain":["database"],
    "node" : ["blockchain", "network"],
    "rpc" : ["node"],
    "node-exe": ["node", "rpc"],
    "node-cint": ["node"]
}

current = sys.argv[1]
deps = deps_graph[current]

for dep in deps:
    package = "%s/0.X@kth/staging" % (dep,)
    print("waiting for %s ..." % (package,))
    res = get_conan_search(package, remote)
    while res != 0:
        print('.', end='')
        sys.stdout.flush()
        time.sleep(1)
        res = get_conan_search(package, remote)
    print("%s found." % (package,))

# conan remove infrastructure/0.X@kth/staging -r kthbuild_kth_temp_
# conan search infrastructure/0.X@kth/staging -r kthbuild_kth_temp_
# conan search infrastructure/0.1.0@kth/testing -r kthbuild_kth_temp_
# conan alias infrastructure/0.X@kth/staging infrastructure/0.1.0@kth/testing
# conan upload infrastructure/0.X@kth/staging -r kthbuild_kth_temp_


# 
# echo "waiting for infrastructure/0.X@kth/staging ..."
# conan search infrastructure/0.X@kth/staging -r kth_temp > $null
# while($env:lastExitCode -eq 1) {
#   Write-Host "."
#   Start-Sleep -s 10
#   conan search infrastructure/0.X@kth/staging -r kth_temp > $null
# }
# Write-Host "infrastructure/0.X@kth/staging found"
