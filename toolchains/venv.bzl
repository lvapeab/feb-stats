def _py_env_toolchain_impl(ctx):
    version = ctx.attr.version.split(".", 2)
    if len(version) != 2:
        fail("Expected version in major.minor format, e.g. 3.7. Found: {}".format(ctx.attr.version))

    py_minor = ctx.actions.declare_file("venv/bin/python{}".format(ctx.attr.version))
    py_major = ctx.actions.declare_file("venv/bin/python{}".format(version[0]))
    python = ctx.actions.declare_file("venv/bin/python")
    venv_cfg = ctx.actions.declare_file("venv/pyvenv.cfg")

    ctx.actions.run(
        executable = ctx.executable._create_venv,
        arguments = [venv_cfg.dirname],
        outputs = [python, py_major, py_minor, venv_cfg],
        use_default_shell_env = True,
    )

    return [
        DefaultInfo(
            executable = py_minor,
            runfiles = ctx.runfiles(
                files = [python, py_major, py_minor, venv_cfg],
            ),
        ),
    ]

py_venv_toolchain = rule(
    implementation = _py_env_toolchain_impl,
    executable = True,
    attrs = {
        "version": attr.string(default = "3.7"),
        "_create_venv": attr.label(
            default = ":create_venv.sh",
            allow_single_file = True,
            executable = True,
            cfg = "target",
        ),
    },
)
