load("@io_bazel_rules_docker//container:image.bzl", "container_image")
load("@io_bazel_rules_docker//python3:image.bzl", "py3_image")
load("@io_bazel_rules_docker//python:image.bzl", "py_layer")
load("@poetry//:dependencies.bzl", "dependency")
load("@rules_python//python:defs.bzl", "py_binary", "py_library", "py_test")

py_library(
    name = "api",
    srcs = glob(
        [
            "api.py",
            "handler.py",
            "codegen/*.py",
        ],
        exclude = ["**/*_test.py"],
    ),
    srcs_version = "PY3",
    visibility = ["//visibility:public"],
    deps = [
        dependency("grpcio"),
        dependency("grpcio-status"),
        dependency("opencensus"),
        "//python/feb_stats:transforms",
        "//python/feb_stats/parsers:feb_parser",
    ],
)

py_test(
    name = "api_test",
    size = "small",
    srcs = [":api_test.py"],
    python_version = "PY3",
    deps = [
        ":api",
    ],
)

py_binary(
    name = "server",
    srcs = ["server.py"],
    main = "server.py",
    visibility = ["//visibility:public"],
    deps = [
        dependency("grpcio-health-checking"),
        dependency("grpcio-reflection"),
        dependency("opencensus-ext-grpc"),
        dependency("opencensus-ext-jaeger"),
        dependency("opencensus-ext-stackdriver"),
        ":api",
    ],
)

py_test(
    name = "server_test",
    srcs = [":server_test.py"],
    deps = [":server"],
)

py_layer(
    name = "externals",
    filter = "@",  # only include labels in external workspaces e.g. @poetry//
    deps = [":server"],
)

py3_image(
    name = "image",
    srcs = [":server"],
    base = "//images:python",
    layers = [
        ":externals",
    ],
    main = "server.py",
    visibility = ["//visibility:public"],
    deps = [],
)
