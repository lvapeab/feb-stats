load("@io_bazel_rules_docker//container:container.bzl", "container_pull")

def image_deps():
    container_pull(
        name = "python3.7.7",
        digest = "sha256:3f51d53c46b50be42513ddeec3892220a7838684002745b41c79e8fc0cca537d",
        registry = "index.docker.io",
        repository = "library/python",
        tag = "3.7.7-slim-buster",
    )
