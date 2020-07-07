load("@rules_python//python:defs.bzl", "py_runtime", "py_runtime_pair")
load(":venv.bzl", "py_venv_toolchain")
load(":wrapper.bzl", "py_wrapper")

py_venv(
    name = "py3_venv",

    # caching the venv interpreter doesn't work for two reasons:
    #
    # * there are no platform dependencies on this target: the cache will contain binaries for the wrong OS
    # * there are no dependencies on the interpreter binary or standard library: the cache may contain stale versions
    #
    # fixing this properly a bit of a pain...
    # the preferred solution is to use a platform specific tarball that does not need to be relocated.
    # unfortunately the Python organization only builds/hosts _installers_ and does not provide binary tarballs.
    # building/maintaining our own binary tarballs is quite a bit of work, if we wait someone else may do it for us.
    # the second best would to add the interpreter and standard library as inputs to the py_venv_toolchain rule.
    # this is not a terrible interim solution, it just needs a repository_rule and a python script to hash
    # said interpreter and libraries, but it's not free and does not provide hermeticicity (binary tarballs would).
    #
    # "no-remote-cache" fixes bullet 1. "no-cache" fixes bullet 1 and mostly avoids bullet 2.
    tags = ["no-cache"],
)

py_wrapper(
    name = "py3_wrapper",
    venv = ":py3_venv",
)

# See: https://github.com/bazelbuild/rules_python/blob/master/docs/python.md

py_runtime(
    name = "py3_runtime",
    files = [":py3_venv"],  # annoying: https://github.com/bazelbuild/bazel/issues/4286
    interpreter = ":py3_wrapper",
    python_version = "PY3",
)

py_runtime_pair(
    name = "py23_runtime_pair",
    py2_runtime = None,
    py3_runtime = ":py3_runtime",
)

toolchain(
    name = "python",
    toolchain = ":py23_runtime_pair",
    toolchain_type = "@bazel_tools//tools/python:toolchain_type",
)

# Container PY3 toolchain

py_runtime(
    name = "container_py3_runtime",
    interpreter_path = "/usr/local/bin/python3.7",
    python_version = "PY3",
)

py_runtime_pair(
    name = "container_py_runtime_pair",
    py2_runtime = None,
    py3_runtime = ":container_py3_runtime",
)

toolchain(
    name = "container_python",
    exec_compatible_with = [
        "@io_bazel_rules_docker//platforms:run_in_container",
    ],
    toolchain = ":container_py_runtime_pair",
    toolchain_type = "@bazel_tools//tools/python:toolchain_type",
)
