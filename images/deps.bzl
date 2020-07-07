load("@io_bazel_rules_docker//container:container.bzl", "container_pull")

def image_deps():
    container_pull(
        name = "python3.7",
        digest = "sha256:57c7d7161fdaa79b61f107b8a480c50657d64dca37295d67db2f675abe38b45a",
        registry = "index.docker.io",
        repository = "library/python",
        tag = "3.7.8",
    )
