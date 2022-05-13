### Workflow
When contributing code, you'll want to follow this checklist:

1. Fork the repository on GitHub.
2. Run the tests to confirm they all pass on your system. If they don't, you'll
   need to investigate why they fail. If you're unable to diagnose this
   yourself, raise it as a bug report by following the guidelines in this
   document: [bug-reports](https://github.com/ostis-ai/py-sc-client/blob/572f26638e4152bb075f026a4533f0d6485e1483/.github/ISSUE_TEMPLATE/bug_report.md).
3. Write tests that demonstrate your bug or feature. Ensure that they fail.
4. Make your change.
5. Run the entire test suite again, confirming that all tests pass *including
   the ones you just added*.
6. Send a GitHub Pull Request to the main repository's ``develop`` branch.
   GitHub Pull Requests are the expected method of code collaboration on this
   project.


This project uses [Git-Flow](https://www.gitkraken.com/learn/git/git-flow),
[git-flow tool](https://github.com/nvie/gitflow) can be used.

The Git flow branches that we are interested in are the following branches :

* `develop` (long lived) - latest development work, deploys to a dev environment
* `feature/*`(short lived) - new functional, docs, build, CI, test development work
* `fix/*`(short lived) - fixes of functional, docs, build, CI, test development work
* `release/*` (short lived) - release candidate, bug fixes for a release, deploys to a test environment
* `main` (long lived) - last release, deploys to a production environment
* `hotfix/*` (short lived) - urgent fixes to production
