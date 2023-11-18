[![Package Release](https://github.com/daniperez/vale-python-package/actions/workflows/python-publish.yml/badge.svg)](https://github.com/daniperez/vale-python-package/actions/workflows/python-publish.yml)

# Vale Python Package

> ⚠️  Vale is a software developed by errata.ai and a community of open-source
> contributors. This repository just makes that software available to Python
> users. The author is not affiliated nor endorsed by errata.ai.

[Vale](https://vale.sh/) is a command-line tool that can enforce an editorial
style guide onto your text. It's written in Go. The purpose of this package is
to allow Python users to have Vale as a dependency of a Python application or
library and this way allow installing Vale without resorting to manual installation
or similar.

## Installation

You can add `vale` package as a dependency in your `setup.py`,
`requirements.txt` or `pyproject.toml` file depending on how are you managing
dependencies. For example, in `requirements.txt`:

```shell
vale==2.29.7
```

The version of this Python package corresponds exactly to Vale's version.  That
is, if you add `vale==2.20.0` as a dependency, Vale with that same version will
be installed.  Note that **Vale as such is not included in this package but
downloaded the first time you execute `vale`**.

## Releasing (only for contributors)

New releases using the last Vale versions are delivered in an automated way.
See [Version Bump if Vale Updated](.github/workflows/check-vale-update.yml) workflow.
The new versions of Vale are checked once a day.

### Manual release 
1. Change version in `pyproject.toml`. Changing the version changes the
   version of Vale that gets downloaded. See note below.
2. Commit & push.
3. Github's Actions will deal with the new release.

Note: Pypi doesn't allow to re-release (even if releases or projects are
deleted). If you want to release this package for a new version of Vale, just
update the `version` attribute found in `pyproject.toml` so that it matches the
version of Vale that you want to release. If something needs to be fixed in
this package, use or increase the 4th number in the version in
`pyproject.toml`.  The 4th number will be ignored when it comes to downloading
Vale but will be used to release the package to PyPi.. For example, if you use
`2.20.0.1`, this package will try to download `vale==2.20.0`. The python
package version will still be `2.20.0.1` in PyPi.
