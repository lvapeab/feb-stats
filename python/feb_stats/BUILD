load("@rules_python//python:defs.bzl", "py_binary", "py_library")
load("@poetry//:dependencies.bzl", "dependency")

py_library(
    name = "utils",
    srcs = [
        "utils.py",
    ],
    srcs_version = "PY3",
    visibility = ["//python:__subpackages__"],
    deps = [
        dependency("pandas"),
    ],
)

py_library(
    name = "locale",
    srcs = [
        "loc.py",
    ],
    srcs_version = "PY3",
    visibility = ["//python:__subpackages__"],
)

py_library(
    name = "entities",
    srcs = [
        "entities.py",
        "entities_ops.py",
    ],
    srcs_version = "PY3",
    visibility = ["//python:__subpackages__"],
    deps = [
        dependency("pandas"),
        ":utils",
    ],
)

py_library(
    name = "transforms",
    srcs = [
        "transforms.py",
    ],
    srcs_version = "PY3",
    visibility = ["//python:__subpackages__"],
    deps = [
        dependency("pandas"),
        ":entities",
        ":utils",
    ],
)

py_library(
    name = "saving",
    srcs = [
        "saving.py",
    ],
    srcs_version = "PY3",
    visibility = ["//python:__subpackages__"],
    deps = [
        dependency("numpy"),
        dependency("pandas"),
        dependency("openpyxl"),
        ":entities",
        ":transforms",
        ":utils",
        "//python/feb_stats/parsers:feb_parser",
    ],
)

[py_test(
    name = file[:-3],
    size = "small",
    srcs = [file],
    srcs_version = "PY3",
    deps = [
        ":entities",
        ":saving",
        ":transforms",
        ":utils",
    ],
) for file in glob(["**/*_test.py"])]
