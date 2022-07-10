"""Push the CI pipeline. Format, create commit from all the changes, push and deploy to PyPi."""

# import os
# import inspect
from pathlib import Path
import sys

# Find paths and add to sys.path to be able to use local version and not installed mypythontools version
# root = Path(os.path.abspath(inspect.getframeinfo(inspect.currentframe()).filename)).parents[1]
root_path_str = Path(__file__).parents[1].as_posix()

if root_path_str not in sys.path:
    sys.path.insert(0, root_path_str)

from mypythontools_cicd.cicd import cicd_pipeline, default_pipeline_config

# default_pipeline_config.test.wsl_virtualenvs = None

default_pipeline_config.deploy = True
default_pipeline_config.test.sync_test_requirements = ["requirements/requirements_tests.txt"]

default_pipeline_config.do_only = "test"
default_pipeline_config.test.virtualenvs = []

if __name__ == "__main__":
    # All the parameters can be overwritten via CLI args
    cicd_pipeline(config=default_pipeline_config)
