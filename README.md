# charasheet

Manage your RPG party & character using an interactive web app accessible from any browser.

[![Test, build, publish & deploy](https://github.com/Crocmagnon/charasheet/actions/workflows/publish.yaml/badge.svg)](https://github.com/Crocmagnon/charasheet/actions/workflows/publish.yaml)

## Quick start
Clone, then
```shell
uv sync
pre-commit install --install-hooks
inv test
./src/manage.py migrate
./src/manage.py loaddata initial_data
./src/manage.py createsuperuser
```

# Reuse
If you do reuse my work, please consider linking back to this repository 🙂
