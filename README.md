# bitprim-ci-utils

Set of functions used in bitprim's continuous integration.

# Requirements

* For the jenkins_utils (debian)
```
apt-get update
apt-get install build-essential -y
apt-get install gcc -y
apt-get install git -y
apt-get install cmake -y
apt-get install python -y
apt-get install python-pip -y
pip install conan --upgrade
pip install conan-package-tools
conan remote add bitprim https://api.bintray.com/conan/bitprim/bitprim
```


# Usage
* jenkins_dependencies.py

```
python jenkins_dependencies.py -rp="/home/hanchon/devel/testing_script/bitprim-node" -p="bitprim-node"
```
