load("@io_bazel_rules_docker//container:image.bzl", "container_image")

container_image(
    name = "python",
    base = "@python3.7//image",
    symlinks = {
        "/usr/bin/python": "/usr/local/bin/python3.7",
        "/usr/bin/python3": "/usr/local/bin/python3.7",
        "/usr/bin/python3.7": "/usr/local/bin/python3.7",
    },
    visibility = [
        "//python:__subpackages__",
    ],
)
