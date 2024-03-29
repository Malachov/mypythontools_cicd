"""Runs before every pytest test. Used automatically (at least at VS Code)."""
from __future__ import annotations
import os
from pathlib import Path
import sys

import pytest

# Find paths and add to sys.path to be able to use local version and not installed mypythontools version
root = Path(__file__).parent.resolve()

if root not in sys.path:
    sys.path.insert(0, root.as_posix())

from mypythontools_cicd.tests import tests_internal as tests
from mypythontools_cicd.project_paths import PROJECT_PATHS

tests.INTERNAL_TESTS_PATH = root
tests.setup_tests()

# Can be loaded from tests here or tests in test project
test_project_path = (
    Path("tests").resolve() / "tested project" if Path.cwd().name != "tested project" else Path.cwd()
)


def prepare_test():
    """This can also been called from tests when running without pytest."""
    os.chdir(test_project_path.as_posix())
    PROJECT_PATHS.reset_paths()


@pytest.fixture(autouse=True)
def prepare_test_fixture():
    """Configure tests. Runs automatically from pytest and is called if running from file."""
    cwd_backup = Path.cwd()

    prepare_test()

    yield

    os.chdir(cwd_backup.as_posix())
