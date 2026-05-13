from pathlib import Path
import subprocess


def read_file(path):

    return Path(path).read_text(
        encoding="utf-8"
    )


def write_file(path, content):

    Path(path).write_text(
        content,
        encoding="utf-8"
    )

    return "file written"


def list_dir(path="."):

    return "\n".join(
        [p.name for p in Path(path).iterdir()]
    )



def glob_files(pattern, path="."):
    base = Path(path)
    return "\n".join([str(p) for p in base.glob(pattern)])


DANGEROUS_PATTERNS = [
    "rm -rf",
    "sudo",
    "shutdown",
    "reboot",
    "mkfs",
    ":(){",
    "chmod -R 777 /",
    "chown -R",
]


def is_dangerous_command(command: str) -> bool:
    command_lower = command.lower()

    for pattern in DANGEROUS_PATTERNS:
        if pattern in command_lower:
            return True

    return False

def exec_command(command):
    if is_dangerous_command(command):
        return "Blocked: dangerous command is not allowed."

    result = subprocess.run(
        command,
        shell=True,
        capture_output=True,
        text=True,
    )

    return result.stdout + result.stderr