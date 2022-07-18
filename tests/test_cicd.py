"""Tests for cicd module."""

# pylint: disable=missing-function-docstring


from __future__ import annotations
from pathlib import Path
import sys
import platform

from mypythontools.system import is_wsl

root_path = sys.path.insert(0, Path(__file__).parents[1].as_posix())  # pylint: disable=no-member

import mypythontools_cicd as cicd
from conftest import prepare_test

test_project_path = Path("tests").resolve() / "tested project"

# pylint: disable=missing-function-docstring,


def test_cicd_pipeline():

    config = cicd.cicd.default_pipeline_config.copy()

    config.git_push = False
    config.git_commit_all = None
    config.version = None
    config.deploy = False
    config.sync_requirements = None
    config.tag = None
    config.allowed_branches = None
    config.test.prepare_test_venvs = None
    config.test.sync_test_requirements = None
    if platform.system() != "Windows" or is_wsl():
        cicd.venvs.prepare_venvs("venv/test_cicd/linux", ["3.10"])
        config.test.update(
            {
                "virtualenvs": ["venv/test_cicd/linux/3.10"],
            }
        )
    else:
        cicd.venvs.prepare_venvs("venv/test_cicd", ["3.10", "wsl-3.10"])
        config.test.update(
            {
                "virtualenvs": ["venv/test_cicd/3.10"],
                "wsl_virtualenvs": ["venv/test_cicd/wsl-3.10"],
            }
        )

    cicd.cicd.cicd_pipeline(config)


if __name__ == "__main__":
    # Find paths and add to sys.path to be able to import local modules
    prepare_test()

    # test_cicd_pipeline()
