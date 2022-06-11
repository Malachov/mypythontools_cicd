"""Tests for cicd module."""

# pylint: disable=missing-function-docstring


from __future__ import annotations
from pathlib import Path
import platform
import sys

from mypythontools.misc import delete_files
from mypythontools.system import is_wsl

root_path = sys.path.insert(0, Path(__file__).parents[1].as_posix())  # pylint: disable=no-member

import mypythontools_cicd as cicd
from mypythontools_cicd.project_paths import PROJECT_PATHS

cicd.tests.setup_tests()

from conftest import prepare_test

test_project_path = Path("tests").resolve() / "tested project"

# pylint: disable=missing-function-docstring,


def test_project_paths():
    cicd.project_paths.PROJECT_PATHS.reset_paths()
    assert cicd.project_paths.PROJECT_PATHS.root == test_project_path
    assert cicd.project_paths.PROJECT_PATHS.init == test_project_path / "project_lib" / "__init__.py"
    assert cicd.project_paths.PROJECT_PATHS.app == test_project_path / "project_lib"
    assert cicd.project_paths.PROJECT_PATHS.docs == test_project_path / "docs"
    assert cicd.project_paths.PROJECT_PATHS.readme == test_project_path / "README.md"
    assert cicd.project_paths.PROJECT_PATHS.tests == test_project_path / "tests"


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

    cicd.project_utils.project_utils_functions.docs_regenerate(keep=("not_deleted.rst",))

    assert rst_path.exists()
    assert another_rst_path.exists()
    assert not_deleted.exists()


def test_reformat_with_black():
    cicd.project_utils.project_utils_functions.reformat_with_black()


def test_set_version():
    cicd.project_utils.project_utils_functions.set_version("0.0.2")
    assert cicd.project_utils.project_utils_functions.get_version() == "0.0.2"
    cicd.project_utils.project_utils_functions.set_version("0.0.1")


def test_build():

    if platform.system() == "Windows" and not is_wsl():

        # Build app with pyinstaller example
        cicd.build.build_app(
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


def test_add_readme_tests():
    for i in PROJECT_PATHS.tests.glob("*"):
        if i.name.startswith("test_readme_generated"):
            i.unlink()

    cicd.tests.add_readme_tests()
    for i in PROJECT_PATHS.tests.glob("*"):
        if i.name.startswith("test_readme_generated"):
            print("Readme tests found.")


def test_project_utils_pipeline():
    config = cicd.project_utils.default_pipeline_config

    config.git_push = False
    config.git_commit_all = None
    config.deploy = False
    config.allowed_branches = None
    config.test = cicd.tests.TestConfig()
    config.test.update({"virtualenvs": [sys.prefix], "wsl_virtualenvs": None, "sync_requirements": None})

    cicd.project_utils.project_utils_pipeline(config)


if __name__ == "__main__":
    # Find paths and add to sys.path to be able to import local modules
    prepare_test()

    # test_cicd()
    # test_build()

    # test_project_utils_pipeline()
