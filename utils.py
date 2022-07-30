# #!/usr/bin/env python

# #
# # Copyright (c) 2019-2022 Knuth Project
# #

# def get_version_from_file():
#     return get_content_default('conan_version')

# def get_version():
#     version = get_version_from_file()

#     if version is None:
#         version = os.getenv("KTH_CONAN_VERSION", None)

#     if version is None:
#         version = get_version_from_branch_name()

#     if version is None:
#         version = get_version_from_git_describe(None, is_development_branch())

#     return version

# def main():
#     get_version()

# if __name__ == "__main__":
#     main()