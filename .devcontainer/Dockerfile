FROM mcr.microsoft.com/devcontainers/python:3.11-bullseye
RUN apt-get update && apt-get upgrade -y
RUN pip install pip-tools invoke
RUN invoke sync-dependencies
RUN pre-commit install --install-hooks
