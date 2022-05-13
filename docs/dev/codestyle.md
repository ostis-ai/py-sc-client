# Style Guide

Python code should be checked on:

- PEP8 code compliance.
- No commented out code.
- Names of classes, functions and variables should reflect the purpose.
- Use snake_case.
- Don't create new files for functions of the same class.
- Code compliance the Python style.
- Decompose tasks. One pull request should not contain many files.
- Cannot copy existing code.
- Follow the DRY principle.

### Self-check

The `isort` tool is used to sort imports.

```sh
isort --line-length 120 path/to/your/files
```

The `black` formatter is used to format the Python code.

```sh
black --line-length 120 path/to/your/files
```

The `pylint` utilities are used to verify the code.

```sh
pylint path/to/your/files
```
