# Vale Python Package

> ⚠️  Vale is a software developed by errata.ai and a community of open-source
> contributors. This repository just makes that software available to Python
> users. The author is not affiliated nor endorsed by errata.ai.

[Vale](https://vale.sh/) is a command-line tool that can enforce an editorial
style guide onto your text. It's written in Go. The purpose of this package is
to allow Python users to have Vale as a dependency.

# Installation 
You can add `vale` package as a dependency in your `setup.py`,
`requirements.txt` or `pyproject.toml` file. 

The versions of this package correspond exactly to Vale's.  That is, if you add
`vale==2.20.0` as a dependency, Vale with that same version will be installed.
Note that Vale as such is not included in this package but downloaded the first
time you execute `vale`.

# Releasing (only for contributors)
## Pre-requisites

python3 -m pip install --upgrade build
python3 -m pip install --upgrade twine

## Releasing
1. Change version
2. python3 -m build
3. python3 -m twine upload --repository testpypi dist/*
   For the username, use __token__. For the password, use the token value, including the pypi- prefix.


Pypi doesn't allow to re-release (even if releases or projects are deleted). 
If something needs to be fixed, increase the 4th number in the version in pyproject.toml. 
