## Installation

Install all project:

```sh
git clone https://github.com/ostis-ai/py-sc-client.git
cd py-sc-client
pip3 install -r requirements-dev.txt
```

Install pre-commit:

```sh
pre-commit install
```

Run tests:
```sh
tox -e py38
```

### Workflow
This project uses [Git-Flow](https://www.gitkraken.com/learn/git/git-flow),
[git-flow tool](https://github.com/nvie/gitflow) can be used.

The Git flow branches that we are interested in are the following branches :

* `develop` (long lived) - latest development work, deploys to a dev environment
* `feature/*`(short lived) - new functional, docs, build, CI, test development work
* `fix/*`(short lived) - fixes of functional, docs, build, CI, test development work
* `release/*` (short lived) - release candidate, bug fixes for a release, deploys to a test environment
* `main` (long lived) - last release, deploys to a production environment
* `hotfix/*` (short lived) - urgent fixes to production
