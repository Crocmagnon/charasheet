# charasheet

## Quick start
Clone, then
```shell
pip install -U pip pip-tools
pip-sync requirements.txt requirements-dev.txt
pre-commit install --install-hooks
inv test
./src/manage.py migrate
./src/manage.py loaddata initial_data
./src/manage.py createsuperuser
```

# Reuse
If you do reuse my work, please consider linking back to this repository 🙂
