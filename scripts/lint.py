import os
import subprocess


def run_command(command: str) -> None:
    try:
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        subprocess.run(command.split(), check=True, cwd=project_root)
    except subprocess.CalledProcessError as e:
        print(f"Error running {command}: {e}")
    return


def main() -> None:
    commands = ["ruff check . --fix", "mypy ."]

    for command in commands:
        run_command(command)
    print("Done")
    return


if __name__ == "__main__":
    main()
