## Setup
This project uses version of Python 3.
It also uses [pipenv](https://pipenv.readthedocs.io/) to manage packages.

To set up this project on your local machine:
1. Clone it from this GitHub repository;
2. Run `pipenv install` from the command line in the project's root directory;


## Running Tests
1. Run tests simply using the `pipenv run python -m pytest -v` command;
2. Use the "-k" option to filter tests by tags:`pipenv run python -m pytest -v -k positive`;
3. You can use tage like: `pipenv run python -m pytest -v -k "positive or negative"`;
4. You can use script line from file Pipfile: `pipenv run tests` = `pipenv run python -m pytest -v`;
5. Run `pipenv run tests_report` for report.


## information
1. File `.env` has information about `BASE_URL`
2. File `Pipfile` has information about dependence [dev-packages, packages] and scripts runner [scripts]
3. File `pytest.ini` has information about pytest: [markers, testpaths]


## Configuration
[pytest-bdd](https://pytest-bdd.readthedocs.io/) to manage BDD (install with pipenv install).