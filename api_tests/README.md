## Setup
This project uses version of Python 3.10.*
It also uses [pipenv](https://pipenv.readthedocs.io/) to manage packages.

To set up this project on your local machine:
1. Clone it from this GitHub repository;
2. Install the appropriate version of python;
3. Install `pipenv` using `pip install pipenv` command;
4. Change directory using `cd api_tests`;
5. Run `pipenv install` to install all needed python dependencies.


## Running Tests
Please make sure you're running the commands from `api_tests` folder.

1. Run tests simply using the `pipenv run python -m pytest -v` command;
2. Use the "-k" option to filter tests by tags:`pipenv run python -m pytest -v -k positive`;
3. You can use tage like: `pipenv run python -m pytest -v -k "positive or negative"`;
4. You can use script line from file Pipfile: `pipenv run tests` = `pipenv run python -m pytest -v`;
5. Run `pipenv run tests_report` for report.
6. Run `pipenv run tests_parallel_report` for report and parallel.


## information
1. File `.env` has information about `BASE_URL`
2. File `Pipfile` has information about dependence [dev-packages, packages] and scripts runner [scripts]
3. File `pytest.ini` has information about pytest: [markers, testpaths]


## Configuration
[pytest-bdd](https://pytest-bdd.readthedocs.io/) to manage BDD (install with pipenv install).