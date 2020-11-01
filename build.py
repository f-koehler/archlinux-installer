from pathlib import Path
import subprocess
import shutil

if __name__ == "__main__":
    build_dir = Path.cwd() / "build"
    iso_dir = Path.cwd() / "isos"
    config_dir = Path.cwd() / "archiso" / "configs" / "releng"

    # build_dir.mkdir(parents=True)
    iso_dir.mkdir(parents=True, exist_ok=True)

    shutil.copytree(config_dir, build_dir, symlinks=True)
