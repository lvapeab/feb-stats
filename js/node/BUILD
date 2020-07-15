load("@build_bazel_rules_nodejs//:index.bzl", "nodejs_binary")
load("@io_bazel_rules_docker//nodejs:image.bzl", "nodejs_image")
load("@io_bazel_rules_docker//container:container.bzl", "container_push")

nodejs_binary(
    name = "app",
    args = [
        "--grpc_port 50001 --port 8080 --grpc_address localhost",
    ],
    data = [
        "server.js",
        "//protos:feb_stats.proto",
        "//js/node/style:main.css",
        "//js/node/style/assets:basketball.png",
        "//js/node/style/assets:intro.svg",
        "//js/node/config:dz_config.js",
        "//js/node/views:index.hbs",
        "//js/node:uploads",
    ] + [
        "@npm//@grpc/proto-loader",
        "@npm//@nestjs/platform-express",
        "@npm//date-format",
        "@npm//express-busboy",
        "@npm//fs-extra",
        "@npm//grpc",
        "@npm//hbs",
        "@npm//yargs",
    ],
    entry_point = "server.js",
    install_source_map_support = False,
)

nodejs_image(
    name = "image",
    args = [
        "--grpc_port",
        "50001",
        "--port",
        "8080",
        "--grpc_address",
        "localhost",
    ],
    data = [
        "server.js",
        "//protos:feb_stats.proto",
        "//js/node/style:main.css",
        "//js/node/style/assets:basketball.png",
        "//js/node/style/assets:intro.svg",
        "//js/node/config:dz_config.js",
        "//js/node/views:index.hbs",
        "//js/node:uploads",
    ] + [
        "@npm//@grpc/proto-loader",
        "@npm//@nestjs/platform-express",
        "@npm//date-format",
        "@npm//express-busboy",
        "@npm//fs-extra",
        "@npm//grpc",
        "@npm//hbs",
        "@npm//yargs",
    ],
    entry_point = "server.js",
    install_source_map_support = False,
)

container_push(
    name = "push_feb-stats_web",
    format = "Docker",
    image = ":image",
    registry = "index.docker.io",
    repository = "lvapeab/feb-stats_web",
    tag = "latest",
)
