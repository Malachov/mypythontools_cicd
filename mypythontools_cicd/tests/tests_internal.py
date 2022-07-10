"""Module with functions for 'tests' subpackage."""

from __future__ import annotations
from typing import Sequence, cast
from pathlib import Path
import sys
import warnings
import os

from typing_extensions import Literal

import mylogging
from mypythontools.paths import validate_path, PathLike, WslPath
from mypythontools.misc import delete_files, print_progress
from mypythontools.config import Config, MyProperty
from mypythontools.system import (
    get_console_str_with_quotes,
    terminal_do_command,
    check_library_is_available,
)

from ..venvs import Venv, prepare_venvs
from ..project_paths import PROJECT_PATHS
from ..packages import get_requirements_files


class TestConfig(Config):
    """Allow to setup tests."""

    @MyProperty
    @staticmethod
    def tested_path() -> None | PathLike:
        """Define path of tested folder.

        Type:
            None | PathLike

        Default:
            None

        If None, root is used. Root is necessary if using doctest, 'tests' folder not works for doctest.
        """
        return None

    @MyProperty
    @staticmethod
    def run_tests() -> bool:
        """Define whether run tests or not.

        Type:
            bool

        Default:
            True
        """
        return True

    @MyProperty
    @staticmethod
    def tests_path() -> None | PathLike:
        """If None, tests is used. It means where venv will be stored etc.

        Type:
            None | PathLike

        Default:
            None
        """
        return None

    @MyProperty
    @staticmethod
    def prepare_test_venvs() -> None | list[str]:
        """Create venvs with defined versions.

        Type:
            None | list[str]

        Default:
            ["3.7", "3.10", "wsl-3.7", "wsl-3.10"]
        """
        return ["3.7", "3.10", "wsl-3.7", "wsl-3.10"]

    @MyProperty
    @staticmethod
    def prepare_test_venvs_path() -> PathLike:
        """Prepare venvs in defined path.

        Type:
            str

        Default:
            "tests/venv"
        """
        return "tests/venv"

    @MyProperty
    @staticmethod
    def test_coverage() -> bool:
        """Whether run test coverage plugin. If True, pytest-cov must be installed.

        Type:
            bool

        Default:
            True
        """
        return True

    @MyProperty
    @staticmethod
    def stop_on_first_error() -> bool:
        """Whether stop on first error.

        Type:
            bool

        Default:
            True
        """
        return True

    @MyProperty
    @staticmethod
    def virtualenvs() -> Sequence[PathLike]:
        """Virtualenvs used to testing. It's used to be able to test more python versions at once.

        Example:
            ``["tests/venvs/3.7", "tests/venvs/3.10"]``. If you want to use current venv, use `[sys.prefix]`.

        Type:
            None | Sequence[PathLike]

        Default:
            ["tests/venv/3.7", "tests/venv/3.10"]

        If no `virtualenvs` nor `wsl_virtualenvs` is configured, then python that called the function
        will be used.
        """
        return ["tests/venv/3.7", "tests/venv/3.10"]

    @MyProperty
    @staticmethod
    def wsl_virtualenvs() -> Sequence[PathLike]:
        """Define which wsl virtual environments will be tested via wsl.

        Type:
            None | Sequence[PathLike]

        Default:
            ["tests/venv/wsl-3.7", "tests/venv/wsl-3.10"]
        """
        return ["tests/venv/wsl-3.7", "tests/venv/wsl-3.10"]

    @MyProperty
    @staticmethod
    def sync_test_requirements() -> None | Literal["infer"] | PathLike | Sequence[PathLike]:
        """Define whether update libraries versions.

        Type:
            None | Literal["infer"] | PathLike | Sequence[PathLike]

        Default:
            ["requirements.txt"]

        If using `virtualenvs` define what libraries will be installed by path to requirements.txt. Can
        also be a list of more files e.g ``["requirements.txt", "requirements_dev.txt"]``. If "infer",
        auto detected (all requirements).
        """
        return ["requirements.txt"]

    @MyProperty
    @staticmethod
    def verbosity() -> Literal[0, 1, 2]:
        """Define whether print details on errors or keep silent.

        Type:
            Literal[0, 1, 2]

        Default:
            1

        If 0, no details, parameters `-q and `--tb=line` are added. if 1, some details are added --tb=short.
        If 2, more details are printed (default --tb=auto).
        """
        return 1

    @MyProperty
    @staticmethod
    def extra_args() -> None | list:
        """List of args passed to pytest.

        Type:
            None | list

        Default:
            None
        """
        return None


default_test_config = TestConfig()


def run_tests(
    config: TestConfig = default_test_config,
) -> None:
    """Run tests. If any test fails, raise an error.

    This is not supposed for normal testing during development. It's usually part of pipeline an runs just
    before pushing code. It usually runs on more python versions and it's syncing dependencies, so takes much
    more time than testing in IDE.

    Args:
        config (PipelineConfig, optional): TestConfig configuration object. Just import default_test_config
            and use intellisense and help tooltip with description. Defaults to `default_test_config`.

    Raises:
        Exception: If any test fail, it will raise exception (git hook do not continue...).

    Note:
        By default args to quiet mode and no traceback are passed. Usually this just runs automatic tests.
        If some of them fail, it's further analyzed in some other tool in IDE.

    Example:
        ``run_tests(verbosity=2)``
    """
    if not config.run_tests:
        return

    print_progress("Testing", config.verbosity > 0)

    tested_path = (
        validate_path(config.tested_path, "Running tests failed", "tested_path")
        if config.tested_path
        else PROJECT_PATHS.root
    )
    tests_path = (
        validate_path(config.tests_path, "Running tests failed", "tests_path")
        if config.tests_path
        else PROJECT_PATHS.tests
    )

    verbosity = config.verbosity
    verbose = True if verbosity == 2 else False
    inner_verbosity = 2 if verbosity == 2 else 0

    extra_args = config.extra_args if config.extra_args else []

    if config.stop_on_first_error:
        extra_args.append("-x")

    if verbosity == 0:
        extra_args.append("-q")
        extra_args.append("--tb=line")
    elif verbosity == 1:
        extra_args.append("--tb=short")

    all_venvs = [*config.virtualenvs, *[f"wsl-{i}" for i in config.wsl_virtualenvs]]
    if not all_venvs:
        all_venvs = [sys.prefix]

    if config.prepare_test_venvs:
        if verbosity:
            print("\tPreparing test venvs")
        prepare_venvs(path=config.prepare_test_venvs_path, versions=config.prepare_test_venvs, verbosity=0)

    for i, venv in enumerate(all_venvs):
        if venv.startswith("wsl-"):
            wsl = True
            venv = venv[4:]
        else:
            wsl = False

        used_path = tested_path if not wsl else WslPath(tested_path).wsl_path
        tested_path_str = get_console_str_with_quotes(used_path)

        complete_args = (
            "pytest",
            tested_path_str,
            *extra_args,
        )

        test_command = " ".join(complete_args)

        used_command = test_command
        if i == 0:
            if config.test_coverage:
                # Add coverage only to first virtualenv
                xml_path = f"xml:{tests_path / 'coverage.xml'}"
                used_command = used_command + (
                    f" --cov {get_console_str_with_quotes(PROJECT_PATHS.app)} --cov-report "
                    f"{get_console_str_with_quotes(xml_path)}"
                )

        my_venv = Venv(venv, with_wsl=wsl)

        if not my_venv.installed:
            raise RuntimeError(
                f"Defined virtualenv on {my_venv.venv_path} not found. Use 'prepare_test_venvs' or install "
                "venvs manually."
            )

        if config.sync_test_requirements:
            if verbosity:
                print(
                    f"\tSyncing requirements in{' wsl ' if wsl else ' '}venv '{my_venv.venv_path.name}' "
                    "for tests"
                )
            my_venv.sync_requirements(
                config.sync_test_requirements,
                ["mypythontools_cicd[tests]"],
                verbosity=inner_verbosity,
            )
        else:
            # To be able to not install dev requirements in older python venv, pytest is installed.
            # Usually just respond with Requirements already satisfied.
            my_venv.install_library("mypythontools_cicd[tests]")

        used_command = f"{my_venv.activate_command} && {test_command}"

        if verbosity:
            print(f"\tStarting tests with {'wsl' if wsl else ''} venv `{venv}`")

        terminal_do_command(
            used_command,
            cwd=tested_path.as_posix(),
            verbose=verbose,
            error_header="Tests failed.",
            with_wsl=wsl,
        )

    if config.test_coverage:
        delete_files(".coverage")


def setup_tests(
    generate_readme_tests: bool = True,
    matplotlib_test_backend: bool = False,
    set_numpy_random_seed: int | None = 2,
) -> None:
    """Add paths to be able to import local version of library as well as other test files.

    Value Mylogging.config.colorize = 0 changed globally.

    Note:
        Function expect `tests` folder on root. If not, test folder will not be added to sys path and
        imports from tests will not work.

    Args:
        generate_readme_tests (bool, optional): If True, generate new tests from readme if there are
            new changes. Defaults to True.
        matplotlib_test_backend (bool, optional): If using matlplotlib, it need to be
            closed to continue tests. Change backend to agg. Defaults to False.
        set_numpy_random_seed (int | None): If using numpy random numbers, it will be each time the same.
            Numpy is not in requirements, so it need to be installed. Defaults to 2.

    """
    mylogging.config.colorize = False

    PROJECT_PATHS.add_root_to_sys_path()

    # Find paths and add to sys.path to be able to import local modules
    test_dir_path = PROJECT_PATHS.tests

    if test_dir_path.as_posix() not in sys.path:
        sys.path.insert(0, test_dir_path.as_posix())

    if matplotlib_test_backend:
        check_library_is_available("matplotlib")
        import matplotlib

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            matplotlib.use("agg")

    if generate_readme_tests:
        add_readme_tests()

    if set_numpy_random_seed:
        import numpy as np

        np.random.seed(2)


def add_readme_tests(readme_path: None | PathLike = None, tests_folder_path: None | PathLike = None) -> None:
    """Generate pytest tests script file from README.md and save it to tests folder.

    Can be called from conftest.

    Args:
        readme_path (None | PathLike, optional): If None, autodetected (README.md, Readme.md or readme.md
            on root). Defaults to None.
        tests_folder_path (None | PathLike, optional): If None, autodetected (if root / tests).
            Defaults to None.

    Raises:
        FileNotFoundError: If Readme not found.

    Example:
        >>> add_readme_tests()

        Readme tests found.

    Note:
        Only blocks with python defined syntax will be evaluated. Example::

            ```python
            import numpy
            ```

        If you want to import modules and use some global variables, add ``<!--phmdoctest-setup-->`` directive
        before block with setup code.
        If you want to skip some test, add ``<!--phmdoctest-mark.skip-->``
    """
    readme_path = (
        validate_path(readme_path, "'add_readme_tests' failed", "README")
        if readme_path
        else PROJECT_PATHS.readme
    )
    tests_folder_path = (
        validate_path(tests_folder_path, "'add_readme_tests' failed", "tests_folder")
        if tests_folder_path
        else PROJECT_PATHS.tests
    )

    readme_date_modified = str(readme_path.stat().st_mtime).split(".", maxsplit=1)[0]  # Keep only seconds
    readme_tests_name = f"test_readme_generated-{readme_date_modified}.py"

    test_file_path = tests_folder_path / readme_tests_name

    # File not changed from last tests
    if test_file_path.exists():
        return

    for i in tests_folder_path.glob("*"):
        if i.name.startswith("test_readme_generated"):
            i.unlink()

    python_path = get_console_str_with_quotes(sys.executable)
    readme = get_console_str_with_quotes(readme_path)
    output = get_console_str_with_quotes(test_file_path)

    generate_readme_test_command = f"{python_path} -m phmdoctest {readme} --outfile {output}"

    terminal_do_command(generate_readme_test_command, error_header="Readme test creation failed")


def deactivate_test_settings() -> None:
    """Deactivate functionality from setup_tests.

    Sometimes you want to run test just in normal mode (enable plots etc.). Usually at the end of
    test file in ``if __name__ = "__main__":`` block.
    """
    mylogging.config.colorize = True

    if "matplotlib" in sys.modules:

        import matplotlib
        from importlib import reload

        reload(matplotlib)
