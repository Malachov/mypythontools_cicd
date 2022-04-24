from __future__ import annotations
from pathlib import Path
import sys

from mypythontools.misc import delete_files

root_path = sys.path.insert(0, Path(__file__).parents[1].as_posix())  # pylint: disable=no-member

from mypythontools_cicd import venvs
from conftest import prepare_test


def test_prepare_venvs():
    delete_files(["3.7", "wsl-3.7"])
    venvs.prepare_venvs(path="venv", versions=["3.7", "3.10", "wsl-3.7", "wsl-3.10"])
    for i in ["3.7", "3.10"]:
        assert venvs.Venv(f"venv/{i}").installed
    for i in ["venv/wsl-3.7", "venv/wsl-3.10"]:
        assert (Path(i) / "bin").exists()


if __name__ == "__main__":
    # Find paths and add to sys.path to be able to import local modules
    # prepare_test()
    # test_prepare_venvs()

    pass
