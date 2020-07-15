load("@rules_python//python:defs.bzl", "py_runtime", "py_runtime_pair")
load(":venv.bzl", "py_venv_toolchain")
load(":wrapper.bzl", "py_wrapper")

py_venv_toolchain(
    name = "py3_venv",
    tags = ["no-cache"],
)

py_wrapper(
    name = "py3_wrapper",
    venv = ":py3_venv",
)

# See: https://github.com/bazelbuild/rules_python/blob/master/docs/python.md
py_runtime(
    name = "py3_runtime",
    files = [":py3_venv"],  # see: https://github.com/bazelbuild/bazel/issues/4286
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
