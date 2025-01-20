from datasets import load_dataset
import subprocess
import re
from parser import MAP_REPO_TO_PARSER

dataset = load_dataset("SWE-Gym/SWE-Gym-Lite", split="train")
NON_TEST_EXTS = [
    ".json",
    ".png",
    "csv",
    ".txt",
    ".md",
    ".jpg",
    ".jpeg",
    ".pkl",
    ".yml",
    ".yaml",
    ".toml",
]
REPO_TO_TEST_CMD = {
  "astropy/astropy": "pytest -rA",
  "django/django": "./tests/runtests.py --verbosity 2 --settings=test_sqlite --parallel 1",
  "matplotlib/matplotlib": "pytest -rA",
  "marshmallow-code/marshmallow": "pytest -rA",
  "mwaskom/seaborn": "pytest --no-header -rA",
  "pallets/flask": "pytest -rA",
  "psf/requests": "pytest -rA",
  "pvlib/pvlib-python": "pytest -rA",
  "pydata/xarray": "pytest -rA",
  "pydicom/pydicom": "pytest -rA",
  "pylint-dev/astroid": "pytest -rA",
  "pylint-dev/pylint": "pytest -rA",
  "pytest-dev/pytest": "pytest -rA",
  "pyvista/pyvista": "pytest -rA",
  "scikit-learn/scikit-learn": "pytest -rA",
  "sphinx-doc/sphinx": "tox --current-env -epy39 -v --",
  "sqlfluff/sqlfluff": "pytest -rA",
  "swe-bench/humaneval": "python",
  "sympy/sympy": "PYTHONWARNINGS='ignore::UserWarning,ignore::SyntaxWarning' bin/test -C --verbose",
  "python/mypy": "pytest -rA -k",
  "getmoto/moto": "pytest -n0 -rA",
  "conan-io/conan": "pytest -n0 -rA",
  "dask/dask": "pytest -n0 -rA  --color=no",
  "project-monai/monai": "pytest -rA ",
  "iterative/dvc": "pytest -rA",
  "bokeh/bokeh": "pytest -rA -n0",
  "modin-project/modin": "pytest -n0 -rA",
  "hypothesisworks/hypothesis": "pytest -n0 -rA --tb=no --no-header",
  "pydantic/pydantic": "pytest -rA --tb=short -vv -o console_output_style=classic --no-header",
  "pandas-dev/pandas": "pytest -rA --tb=long",
  "facebookresearch/hydra": "pytest -rA --tb=long"
}
def count_helper(d, value):
    count = 0
    for key, val in d.items():
        if val == value:
            count += 1
    return count

def get_test_directives(instance: dict) -> list:

    # Get test directives from test patch and remove non-test files
    diff_pat = r"diff --git a/.* b/(.*)"
    test_patch = instance["test_patch"]
    directives = re.findall(diff_pat, test_patch)
    directives = [
        d for d in directives if not any(d.endswith(ext) for ext in NON_TEST_EXTS)
    ]
    print(directives)

def get_verification_script(repo, commit_id):
    instance = dataset.filter(lambda x: x["repo"] == repo and x["base_commit"] == commit_id)[0]
    if instance['repo'] == "python/mypy":
        pattern = r'\[case ([^\]]+)\]'
        test_keys = re.findall(pattern, instance["test_patch"])
        test_keys_or = " or ".join(test_keys)
        test_command = REPO_TO_TEST_CMD[repo] + " " + f'"{test_keys_or}"'
        cmd_list = test_command.split(" ")
    else:
        cmd_list = REPO_TO_TEST_CMD[repo].split(" ")
        for test in instance["PASS_TO_PASS"]:
            if "[" in test and "]" not in test:
                continue
            cmd_list.append(test)
    print(" ".join(cmd_list))
    output = subprocess.run(cmd_list, capture_output=True)
    print(output.stdout)
    output = output.stdout.decode("utf-8")
    parser = MAP_REPO_TO_PARSER[repo]
    result = parser(output)
    num_passed = count_helper(result, "PASSED")
    num_failed = count_helper(result, "FAILED")
    print("RESULT: \n\n" + str(result))
    print(f"SUCCESS RATE: {(num_passed / (num_passed + num_failed)) * 100}% ({num_passed} passed, {num_failed} failed)")
    return result

get_verification_script("getmoto/moto", "b2300f1eae1323e3e8bc45f97e530ce129dff12e")