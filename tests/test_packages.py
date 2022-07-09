"""Tests for cicd module."""

# pylint: disable=missing-function-docstring


from __future__ import annotations
from pathlib import Path
import sys

root_path = sys.path.insert(0, Path(__file__).parents[1].as_posix())  # pylint: disable=no-member

from mypythontools_cicd import packages
from conftest import prepare_test

test_project_path = Path("tests").resolve() / "tested project"

# pylint: disable=missing-function-docstring,


def test_set_version():
    assert packages.get_version() == "0.0.1"
    packages.set_version("0.0.2")
    assert packages.get_version() == "0.0.2"
    packages.set_version("0.0.1")


if __name__ == "__main__":
    # Find paths and add to sys.path to be able to import local modules
    prepare_test()

    test_set_version()
