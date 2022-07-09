"""Tests for cicd module."""

# pylint: disable=missing-function-docstring


from __future__ import annotations
from pathlib import Path
import sys


root_path = sys.path.insert(0, Path(__file__).parents[1].as_posix())  # pylint: disable=no-member

from mypythontools_cicd import docs
from conftest import prepare_test

test_project_path = Path("tests").resolve() / "tested project"

# pylint: disable=missing-function-docstring,


def test_docs_regenerate():
    rst_path = test_project_path / "docs" / "source" / "project_lib.rst"
    another_rst_path = test_project_path / "docs" / "source" / "content" / "also_not_deleted.rst"
    not_deleted = test_project_path / "docs" / "source" / "not_deleted.rst"

    if rst_path.exists():
        rst_path.unlink()  # missing_ok=True from python 3.7 on...

    if not not_deleted.exists():
        with open(not_deleted, "w") as not_deleted_file:
            not_deleted_file.write("I will not be deleted.")
            # missing_ok=True from python 3.7 on...

    docs.docs_regenerate(keep=("not_deleted.rst",))

    assert rst_path.exists()
    assert another_rst_path.exists()
    assert not_deleted.exists()


if __name__ == "__main__":
    # Find paths and add to sys.path to be able to import local modules
    prepare_test()

    # test_docs_regenerate()
