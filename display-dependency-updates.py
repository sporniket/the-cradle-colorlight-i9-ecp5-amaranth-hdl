import glob
import subprocess
import sys
from rich import print
from rich.console import Console
from rich.markdown import Markdown


def fetchLastHash(url: str, branch: str) -> str:
    runResult = subprocess.run(
        ["git", "ls-remote", url, branch], capture_output=True, text=True
    )
    runResult.check_returncode()  # abort on error
    return runResult.stdout.split()[0]


def genDependencyLine(package: str, url: str, branch: str) -> None:
    print(f"    '{package} @ git+{url}@{fetchLastHash(url,branch)}',")


def genDependencyLineWorkflow(package: str, url: str, branch: str) -> None:
    print(f"        pip install '{package} @ git+{url}@{fetchLastHash(url,branch)}',")


cn = Console()
cn.print(Markdown("# pyproject.toml updates"))
genDependencyLine(
    "amaranth-stuff-by-sporniket", "https://github.com/sporniket/amaranth-stuff", "main"
)
