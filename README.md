# aws-utils

## Prepare build environment
```
virtualenv -p python3 .venv
. .venv/bin/activate
pip install --upgrade pip
pip install build
```

## Build the wheel or install locally
```
python -m build --wheel
pip install -e .
```

## Test
```
aws-login
```