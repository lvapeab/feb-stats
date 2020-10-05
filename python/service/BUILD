load("@io_bazel_rules_docker//container:image.bzl", "container_image")
load("@io_bazel_rules_docker//container:container.bzl", "container_push")
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
        "//python/feb_stats:locale",
        "//python/feb_stats:saving",
        "//python/feb_stats:transforms",
        "//python/feb_stats/parsers:feb_parser",
    ],
)

py_test(
    name = "api_test",
    size = "small",
    srcs = [":api_test.py"],
    data = [
        "//test_data:1.html",
        "//test_data:2.html",
    ],
    python_version = "PY3",
    deps = [
        ":api",
    ],
)

py_binary(
    name = "server",
    srcs = ["webapp.py"],
    main = "webapp.py",
    visibility = ["//visibility:public"],
    deps = [
        dependency("grpcio-reflection"),
        dependency("opencensus-ext-grpc"),
        dependency("opencensus-ext-jaeger"),
        dependency("opencensus-ext-prometheus"),
        ":api",
    ],
)

py_test(
    name = "server_test",
    size = "small",
    srcs = [":server_test.py"],
    deps = [":server"],
)

py3_image(
    name = "image",
    srcs = ["webapp.py"],
    base = "//images:python",
    main = "webapp.py",
    visibility = ["//visibility:public"],  # TODO: Constrain the visibility
    deps = [
        ":api",
        ":server",
    ],
)

container_push(
    name = "push_feb-stats",
    format = "Docker",
    image = ":image",
    registry = "index.docker.io",
    repository = "lvapeab/feb-stats",
    tag = "latest",
)
