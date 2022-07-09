"""Tests for cicd module."""

# pylint: disable=missing-function-docstring


from __future__ import annotations
from pathlib import Path
import sys

root_path = sys.path.insert(0, Path(__file__).parents[1].as_posix())  # pylint: disable=no-member

from mypythontools_cicd import tests
from mypythontools_cicd.project_paths import PROJECT_PATHS
from conftest import prepare_test

test_project_path = Path("tests").resolve() / "tested project"

# pylint: disable=missing-function-docstring,


def test_add_readme_tests():
    for i in PROJECT_PATHS.tests.glob("*"):
        if i.name.startswith("test_readme_generated"):
            i.unlink()

    tests.add_readme_tests()
    for i in PROJECT_PATHS.tests.glob("*"):
        if i.name.startswith("test_readme_generated"):
            print("Readme tests found.")


if __name__ == "__main__":
    # Find paths and add to sys.path to be able to import local modules
    prepare_test()

    # test_add_readme_tests()
