load("@rules_python//python:defs.bzl", "py_binary")
load("@poetry//:dependencies.bzl", "dependency")

package(default_visibility = ["//python:__subpackages__"])

py_binary(
    name = "export_boxscores",
    srcs = [
        "export_boxscores.py",
    ],
    main = "export_boxscores.py",
    srcs_version = "PY3",
    deps = [
        "//python/feb_stats:saving",
        "//python/feb_stats:transforms",
        "//python/feb_stats/parsers:feb_parser",
    ],
)

py_binary(
    name = "save_server_response",
    srcs = [
        "save_server_response.py",
    ],
    main = "save_server_response.py",
    srcs_version = "PY3",
)
