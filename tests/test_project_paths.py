"""Tests for cicd module."""

# pylint: disable=missing-function-docstring


from __future__ import annotations
from pathlib import Path
import sys

root_path = sys.path.insert(0, Path(__file__).parents[1].as_posix())  # pylint: disable=no-member

from mypythontools_cicd.project_paths import PROJECT_PATHS
from conftest import prepare_test

test_project_path = Path("tests").resolve() / "tested project"

# pylint: disable=missing-function-docstring,


def test_project_paths():
    PROJECT_PATHS.reset_paths()
    assert PROJECT_PATHS.root == test_project_path
    assert PROJECT_PATHS.init == test_project_path / "project_lib" / "__init__.py"
    assert PROJECT_PATHS.app == test_project_path / "project_lib"
    assert PROJECT_PATHS.docs == test_project_path / "docs"
    assert PROJECT_PATHS.readme == test_project_path / "README.md"
    assert PROJECT_PATHS.tests == test_project_path / "tests"


if __name__ == "__main__":
    # Find paths and add to sys.path to be able to import local modules
    prepare_test()

    # test_project_paths()
