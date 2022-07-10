from __future__ import annotations
from pathlib import Path
import sys
import platform

from mypythontools.misc import delete_files
from mypythontools.system import is_wsl

root_path = sys.path.insert(0, Path(__file__).parents[1].as_posix())  # pylint: disable=no-member

from conftest import prepare_test
from mypythontools_cicd import venvs


def test_prepare_venvs():

    if platform.system() == "Windows" and not is_wsl:
        delete_files(["3.7", "wsl-3.7"])
        venvs.prepare_venvs(path="venv", versions=["3.7", "3.10", "wsl-3.7", "wsl-3.10"])
        for i in ["3.7", "3.10"]:
            assert venvs.Venv(f"venv/{i}").installed
        for i in ["venv/wsl-3.7", "venv/wsl-3.10"]:
            assert (Path(i) / "bin").exists()

    # TODO test with_wsl


if __name__ == "__main__":
    # Find paths and add to sys.path to be able to import local modules
    prepare_test()
