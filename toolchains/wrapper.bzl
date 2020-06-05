def _impl(ctx):
    wrapper = ctx.actions.declare_file("py3wrapper.sh")

    # we are required to create a new file when returning an executable...
    # so even though no substitutions are being made this seems about the same
    # as running `cp`
    ctx.actions.expand_template(
        template = ctx.file._template,
        output = wrapper,
        is_executable = True,
        substitutions = {},
    )

    return [
        DefaultInfo(
            executable = wrapper,
            runfiles = ctx.runfiles(
                files = [wrapper],
                transitive_files = depset(ctx.files.venv),
            ),
        ),
    ]

py_wrapper = rule(
    implementation = _impl,
    executable = True,
    attrs = {
        "venv": attr.label(
            mandatory = True,
            executable = True,
            cfg = "target",
        ),
        "_template": attr.label(
            default = ":py3wrapper.sh",
            allow_single_file = True,
        ),
    },
)
