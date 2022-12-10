# charasheet

## Quick start
Clone, then
```shell
pyenv virtualenv 3.11.1 charasheet
pyenv local charasheet
pip install pip-tools
pip-sync requirements.txt requirements-dev.txt
pre-commit install --install-hooks
inv test
./src/manage.py migrate
./src/manage.py loaddata initial_data
./src/manage.py createsuperuser
```
