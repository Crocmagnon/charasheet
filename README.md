# charasheet

Manage your RPG party & character using an interactive web app accessible from any browser.

## Quick start
Clone, then
```shell
pip install -U pip pip-tools invoke
inv sync-dependencies
pre-commit install --install-hooks
inv test
./src/manage.py migrate
./src/manage.py loaddata initial_data
./src/manage.py createsuperuser
```

## With preview mode

```shell
caddy --config contrib/Caddyfile.local
./src/manage.py runserver
cd ~/Projects/charasheet-go
make run/live
```

# Reuse
If you do reuse my work, please consider linking back to this repository 🙂
