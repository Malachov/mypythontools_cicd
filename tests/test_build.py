"""Tests for cicd module."""

# pylint: disable=missing-function-docstring


from __future__ import annotations
from pathlib import Path
import platform
import sys

from mypythontools.misc import delete_files
from mypythontools.system import is_wsl

root_path = sys.path.insert(0, Path(__file__).parents[1].as_posix())  # pylint: disable=no-member

from mypythontools_cicd import build


from conftest import prepare_test

test_project_path = Path("tests").resolve() / "tested project"

# pylint: disable=missing-function-docstring,


def test_build():

    if platform.system() == "Windows" and not is_wsl():

        # Build app with pyinstaller example
        build.build_app(
            main_file="app.py",
            console=True,
            debug=True,
            clean=False,
            build_web=False,
            ignored_packages=["matplotlib"],
            virtualenv=sys.prefix,
            sync_requirements=None,
        )

        assert (test_project_path / "dist").exists()

        delete_files(test_project_path / "build")
        delete_files(test_project_path / "dist")


if __name__ == "__main__":
    # Find paths and add to sys.path to be able to import local modules
    prepare_test()

    # test_build()
