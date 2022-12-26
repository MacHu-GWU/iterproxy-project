# -*- coding: utf-8 -*-

import sys
import subprocess
from pathlib import Path

dir_project_root = Path(__file__).absolute().parent.parent.parent

# code structure
dir_tests = dir_project_root / "tests"
dir_htmlcov = dir_project_root / "htmlcov"
path_cov_index_html = dir_htmlcov / "index.html"

# virtual environment
dir_bin = Path(sys.executable).parent
bin_pytest = dir_bin / "pytest"


def _run_cov_test(
    bin_pytest: str,
    script: str,
    module: str,
    root_dir: str,
    htmlcov_dir: str,
):
    """
    A simple wrapper around pytest + coverage cli command.

    :param bin_pytest: the path to pytest executable
    :param script: the path to test script
    :param module: the dot notation to the python module you want to calculate
        coverage
    :param root_dir: the dir to dump coverage results binary file
    :param htmlcov_dir: the dir to dump HTML output
    """
    args = [
        bin_pytest,
        "-s",
        "--tb=native",
        f"--rootdir={root_dir}",
        f"--cov={module}",
        "--cov-report",
        "term-missing",
        "--cov-report",
        f"html:{htmlcov_dir}",
        script,
    ]
    subprocess.run(args)


def run_cov_test(script: str, module: str, preview: bool = False):
    _run_cov_test(
        bin_pytest=f"{bin_pytest}",
        script=script,
        module=module,
        root_dir=f"{dir_project_root}",
        htmlcov_dir=f"{dir_htmlcov}",
    )
    if preview:
        subprocess.run(["open", f"{path_cov_index_html}"])
