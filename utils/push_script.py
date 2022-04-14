"""Push the CI pipeline. Format, create commit from all the changes, push and deploy to PyPi."""

# import os
# import inspect
from pathlib import Path
import sys

# Find paths and add to sys.path to be able to use local version and not installed mypythontools version
root_path_str = Path(__file__).parents[1].as_posix()
# root = Path(os.path.abspath(inspect.getframeinfo(inspect.currentframe()).filename)).parents[1]

if root_path_str not in sys.path:
    sys.path.insert(0, root_path_str)

from mypythontools_cicd.project_utils import project_utils_pipeline, DEFAULT_PIPELINE_CONFIG

DEFAULT_PIPELINE_CONFIG.deploy = True
# DEFAULT_PIPELINE_CONFIG.do_only = ""


if __name__ == "__main__":
    # All the parameters can be overwritten via CLI args
    project_utils_pipeline(config=DEFAULT_PIPELINE_CONFIG)
