load("@rules_python//python:defs.bzl", "py_binary", "py_library")
load("@poetry//:dependencies.bzl", "dependency")

py_library(
    name = "generic_parser",
    srcs = [
        "generic_parser.py",
    ],
    srcs_version = "PY3",
    visibility = ["//python:__subpackages__"],
    deps = [
        dependency("lxml"),
        dependency("requests"),
        "//python/feb_stats:entities",
    ],
)

py_library(
    name = "feb_parser",
    srcs = [
        "feb_parser.py",
        "feb_stats_transforms.py",
    ],
    srcs_version = "PY3",
    visibility = ["//python:__subpackages__"],
    deps = [
        dependency("numpy"),
        dependency("pandas"),
        ":generic_parser",
    ],
)

[py_test(
    name = file[:-3],
    size = "small",
    srcs = [file],
    data = [
        "//test_data:1.html",
    ],
    srcs_version = "PY3",
    deps = [
        ":feb_parser",
    ],
) for file in glob(["**/*_test.py"])]
