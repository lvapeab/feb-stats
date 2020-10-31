load("@io_bazel_rules_docker//container:image.bzl", "container_image")
load("@io_bazel_rules_docker//container:container.bzl", "container_push")
load("@io_bazel_rules_docker//python3:image.bzl", "py3_image")
load("@io_bazel_rules_docker//python:image.bzl", "py_layer")
load("@poetry//:dependencies.bzl", "dependency")
load("@rules_python//python:defs.bzl", "py_binary", "py_library", "py_test")

py_binary(
    name = "webapp",
    srcs = ["webapp.py"],
    data = [
        "//js/node/config:dz_config.js",
        "//python/web:uploads",
        "//python/web/config:local.yaml",
        "//python/web/static:main.css",
        "//python/web/static/assets:basketball.png",
        "//python/web/static/assets:intro.svg",
        "//python/web/templates:index.html",
    ],
    main = "webapp.py",
    visibility = ["//visibility:public"],
    deps = [
        dependency("pyyaml"),
        dependency("flask"),
        dependency("werkzeug"),
        "//python/service:api",
        "//python/service:server",
    ],
)

[py_test(
    name = file[:-3],
    size = "small",
    srcs = [file],
    srcs_version = "PY3",
    deps = [
        ":webapp",
    ],
) for file in glob(["**/*_test.py"])]

#py3_image(
#    name = "image",
#    srcs = ["server.py"],
#    base = "//images:python",
#    main = "server.py",
#    visibility = ["//visibility:public"],  # TODO: Constrain the visibility
#    deps = [
#        ":api",
#        ":server",
#    ],
#)
#
#container_push(
#    name = "push_feb-stats",
#    format = "Docker",
#    image = ":image",
#    registry = "index.docker.io",
#    repository = "lvapeab/feb-stats",
#    tag = "latest",
#)
