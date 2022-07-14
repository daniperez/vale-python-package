# Pre-requisites

python3 -m pip install --upgrade build
python3 -m pip install --upgrade twine

# Releasing
1. Change version
2. python3 -m build
3. python3 -m twine upload --repository testpypi dist/*
   For the username, use __token__. For the password, use the token value, including the pypi- prefix.


Pypi doesn't allow to re-release (even if releases or projects are deleted). 
If something needs to be fixed, increase the 4th number in the version in pyproject.toml. 
