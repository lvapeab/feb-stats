workspace(
    name = "feb_stats",
    managed_directories = {
        "@npm": ["node_modules"],
    },
)

# register local toolchains before loading other workspaces
register_toolchains("//toolchains:container_python")

register_toolchains("//toolchains:python")

register_execution_platforms(
    "@local_config_platform//:host",
    "@io_bazel_rules_docker//platforms:local_container_platform",
)

load("@bazel_tools//tools/build_defs/repo:http.bzl", "http_archive")

# Packaging rules
http_archive(
    name = "rules_pkg",
    sha256 = "352c090cc3d3f9a6b4e676cf42a6047c16824959b438895a76c2989c6d7c246a",
    url = "https://github.com/bazelbuild/rules_pkg/releases/download/0.2.5/rules_pkg-0.2.5.tar.gz",
)

# Python rules
http_archive(
    name = "rules_python",
    sha256 = "c911dc70f62f507f3a361cbc21d6e0d502b91254382255309bc60b7a0f48de28",
    strip_prefix = "rules_python-38f86fb55b698c51e8510c807489c9f4e047480e",
    urls = ["https://github.com/bazelbuild/rules_python/archive/38f86fb55b698c51e8510c807489c9f4e047480e.tar.gz"],
)

load("@rules_python//python:repositories.bzl", "py_repositories")

py_repositories()

# Poetry rules for managing Python dependencies
http_archive(
    name = "com_sonia_rules_poetry",
    sha256 = "8a7a6a5d2ef859ba4309929f3b4d61031f2a4bfed6f450f04ab09443246a4b5c",
    strip_prefix = "rules_poetry-ecd0d9c66b89403667304b11da3bd99764797a63",
    urls = ["https://github.com/soniaai/rules_poetry/archive/ecd0d9c66b89403667304b11da3bd99764797a63.tar.gz"],
)

load("@com_sonia_rules_poetry//rules_poetry:defs.bzl", "poetry_deps")

poetry_deps()

load("@com_sonia_rules_poetry//rules_poetry:poetry.bzl", "poetry")

poetry(
    name = "poetry",
    excludes = [
        "enum34",
        "functools32",
        "pywin32",
        "setuptools",
    ],
    lockfile = "//python:poetry.lock",
    pyproject = "//python:pyproject.toml",
    tags = ["no-remote-cache"],  # optional, if you would like to pull from pip instead of a Bazel cache
)

# Docker rules
http_archive(
    name = "io_bazel_rules_docker",
    sha256 = "363a8b03f7af8bdd5b44a9d4e19566870b520f8c155fb72837f7fd4a3bdc2538",
    strip_prefix = "rules_docker-2ae5f7f0c43b7efd32a4d7f927bb701f060972af",  # v0.14.4 version is buggy (https://github.com/bazelbuild/rules_docker/issues/1550)
    urls = ["https://github.com/bazelbuild/rules_docker/archive/2ae5f7f0c43b7efd32a4d7f927bb701f060972af.zip"],
)

load(
    "@io_bazel_rules_docker//repositories:repositories.bzl",
    container_repositories = "repositories",
)

container_repositories()

load("@io_bazel_rules_docker//repositories:deps.bzl", container_deps = "deps")

container_deps()

load("@io_bazel_rules_docker//repositories:pip_repositories.bzl", "pip_deps")

pip_deps()

load(
    "@io_bazel_rules_docker//python3:image.bzl",
    _py_image_repos = "repositories",
)

_py_image_repos()

load("//images:deps.bzl", "image_deps")

image_deps()

# NodeJS rules
http_archive(
    name = "build_bazel_rules_nodejs",
    sha256 = "f9e7b9f42ae202cc2d2ce6d698ccb49a9f7f7ea572a78fd451696d03ef2ee116",
    urls = ["https://github.com/bazelbuild/rules_nodejs/releases/download/1.6.0/rules_nodejs-1.6.0.tar.gz"],
)

load("@build_bazel_rules_nodejs//:index.bzl", "node_repositories", "yarn_install")

# The yarn_install rule runs yarn anytime the package.json or yarn.lock file changes.
# It also extracts and installs any Bazel rules distributed in an npm package.
yarn_install(
    name = "npm",  # Name this npm so that Bazel Label references look like @npm//package
    package_json = "//:package.json",
    yarn_lock = "//:yarn.lock",
)
