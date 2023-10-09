from glob import glob
import os
import shutil
from rich import print

for pattern in ["tmp.test_*", "build-tests/*", "build/*", "dist/*", "test_*"]:
    print(f"   [yellow]Cleaning[/yellow] {pattern}...")
    for path in glob(pattern, recursive=0):
        print(f"   :wastebasket: [bright_black]{path}[/bright_black]")
        if os.path.isdir(path):
            shutil.rmtree(path)
        else:
            os.remove(path)

for path in [".coverage", "htmlcov", ".pytest_cache"]:
    if os.path.exists(path):
        print(f"   [yellow]Removing[/yellow] {path}...")
        if os.path.isdir(path):
            shutil.rmtree(path)
        else:
            os.remove(path)

print(f":white_check_mark: [bold green]DONE Cleaning.[/bold green]")
