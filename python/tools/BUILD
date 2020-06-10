load("@rules_python//python:defs.bzl", "py_binary")
load("@poetry//:dependencies.bzl", "dependency")

package(default_visibility = ["//python:__subpackages__"])

py_binary(
    name = "launch_gui",
    srcs = [
        "launch_gui.py",
    ],
    main = "launch_gui.py",
    srcs_version = "PY3",
    deps = [
        "//python/feb_stats:parser",
        "//python/feb_stats:transforms",
    ],
)

py_binary(
    name = "analyze_boxscores",
    srcs = [
        "analyze_boxscores.py",
    ],
    main = "analyze_boxscores.py",
    srcs_version = "PY3",
    deps = [
        "//python/feb_stats:entities_ops",
        "//python/feb_stats:parser",
        "//python/feb_stats:transforms",
    ],
)
