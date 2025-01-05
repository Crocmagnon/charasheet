from pathlib import Path

from invoke import Context, task

BASE_DIR = Path(__file__).parent.resolve(strict=True)
SRC_DIR = BASE_DIR / "src"
COMPOSE_BUILD_FILE = BASE_DIR / "docker-compose-build.yaml"
COMPOSE_BUILD_ENV = {"COMPOSE_FILE": COMPOSE_BUILD_FILE}
TEST_ENV = {"ENV_FILE": BASE_DIR / "envs" / "test-envs.env"}


@task
def update_dependencies(ctx: Context):
    with ctx.cd(BASE_DIR):
        ctx.run("uv lock --upgrade", pty=True, echo=True)


@task
def sync_dependencies(ctx: Context):
    with ctx.cd(BASE_DIR):
        ctx.run("uv sync", pty=True, echo=True)


@task
def makemessages(ctx: Context):
    with ctx.cd(SRC_DIR):
        ctx.run("./manage.py makemessages -l en -l fr", pty=True, echo=True)


@task
def compilemessages(ctx: Context):
    with ctx.cd(SRC_DIR):
        ctx.run("./manage.py compilemessages -l en -l fr", pty=True, echo=True)


@task
def test(ctx: Context):
    with ctx.cd(SRC_DIR):
        ctx.run("pytest", pty=True, echo=True, env=TEST_ENV)


@task
def test_cov(ctx: Context):
    with ctx.cd(SRC_DIR):
        ctx.run(
            "pytest --cov=. --cov-branch --cov-report term-missing:skip-covered",
            pty=True,
            echo=True,
            env={"COVERAGE_FILE": BASE_DIR / ".coverage"},
        )


@task
def download_db(ctx: Context):
    with ctx.cd(BASE_DIR):
        ctx.run(
            "scp ubuntu:/mnt/data/charasheet/db/db.sqlite3 ./db/db.sqlite3",
            pty=True,
            echo=True,
        )
        ctx.run("rm -rf src/media/", pty=True, echo=True)
        ctx.run(
            "scp -r ubuntu:/mnt/data/charasheet/media/ ./src/media",
            pty=True,
            echo=True,
        )
    with ctx.cd(SRC_DIR):
        ctx.run("./manage.py changepassword gaugendre", pty=True, echo=True)


@task
def dump_initial(ctx: Context):
    with ctx.cd(SRC_DIR):
        path = "./character/fixtures/initial_data.json"
        ctx.run(
            f"./manage.py dumpdata character --natural-primary --natural-foreign -e character.Character -o {path} --indent 2",
            pty=True,
            echo=True,
        )
        ctx.run(f"pre-commit run pretty-format-json --file {path}", pty=True, echo=True)


@task
def import_from_co_drs(ctx: Context):
    with ctx.cd(SRC_DIR):
        ctx.run("./manage.py import_races", pty=True, echo=True)
        ctx.run("./manage.py import_profiles", pty=True, echo=True)
        ctx.run("./manage.py import_paths", pty=True, echo=True)
        ctx.run("./manage.py import_capabilities", pty=True, echo=True)
        ctx.run("./manage.py import_harmful_states", pty=True, echo=True)
        ctx.run("./manage.py import_weapons", pty=True, echo=True)


@task(pre=[import_from_co_drs, dump_initial])
def update_fixtures(_: Context):
    pass
