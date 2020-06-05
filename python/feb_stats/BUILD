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
    name = "entities",
    srcs = [
        "entities.py",
    ],
    srcs_version = "PY3",
    visibility = ["//python:__subpackages__"],
    deps = [
        dependency("numpy"),
        dependency("pandas"),
        dependency("xlsxwriter"),
        ":utils",
    ],
)

py_library(
    name = "transforms",
    srcs = [
        "cum_stats_transforms.py",
        "game_stats_transforms.py",
        "transforms.py",
    ],
    srcs_version = "PY3",
    visibility = ["//python:__subpackages__"],
    deps = [
        ":entities",
    ],
)

py_library(
    name = "parser",
    srcs = [
        "parser.py",
    ],
    srcs_version = "PY3",
    visibility = ["//python:__subpackages__"],
    deps = [
        dependency("lxml"),
        dependency("requests"),
        ":entities",
        ":transforms",
    ],
)

[py_test(
    name = file[:-3],
    size = "small",
    srcs = [file],
    srcs_version = "PY3",
    deps = [
        ":entities",
        ":parser",
        ":transforms",
        ":utils",
    ],
) for file in glob(["**/*_test.py"])]
