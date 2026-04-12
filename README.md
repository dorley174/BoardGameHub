## Contributors

| Name   | Mail                   | Telegram alias | Github nickname|
|-----------------|--------------------------|----------------|----------------|
| Danil Valiev | d.valiev@innopolis.university | @dorley  | Dorley174 |
| Egor Savchenko | e.savchenko@innopolis.university | @KOSMOGOR | KOSMOGOR |
| Valeria Kolesnikova| v.kolesnikova@innopolis.university | @Codekd | cdeth567 |
| Nikita Solomennikov | n.solomennikov@innopolis.university | @Hiksol | Hiksol |
| Bulat Shigapov | b.shigapov@innopolis.university | @blt326Ray | Ray3264 |

## Installation

This project uses [Poetry](https://python-poetry.org/) for dependency management.

### Step-by-step (terminal)

1. Install Poetry using the command for your operating system (see **One-time: install Poetry** below).
2. Change to the repository root directory.
3. Run `poetry install` to create the virtual environment and install all dependencies from the lock file.
4. Start the API with `poetry run uvicorn src.main:app --reload`.
5. Optional: open a second terminal, `cd` to the same directory, and run `poetry run streamlit run streamlit_app.py` for the demo UI.
6. For tests or linters, use `poetry run pytest`, `poetry run flake8 …`, and so on (see **Quality Control**).

### One-time: install Poetry

**Windows (PowerShell):**

```powershell
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -
```

**macOS / Linux:**

```bash
curl -sSL https://install.python-poetry.org | python3 -
```

Add Poetry to your `PATH` if the installer prompts you to. Verify:

```bash
poetry --version
```

### Create the environment and install dependencies

From the repository root:

```bash
poetry install
```

This creates a virtual environment (under Poetry’s cache or, if configured, in-project) and installs runtime + dev dependencies from `pyproject.toml` / `poetry.lock`.

### Run the API and Streamlit UI

Start the API (repository root):

```bash
poetry run uvicorn src.main:app --reload
```

Streamlit demo (separate terminal):

```bash
poetry run streamlit run streamlit_app.py
```

Other common commands:

```bash
poetry run pytest
poetry run flake8 src tests streamlit_app.py
poetry run bandit -r src -c .bandit -lll
poetry run radon cc -a -s src
```

To open a shell **inside** the Poetry environment:

```bash
poetry shell
```

After `poetry shell`, you can run `uvicorn`, `pytest`, etc. without the `poetry run` prefix.

### Optional: export requirements for non-Poetry tools

Poetry 2.x needs the export plugin once:

```bash
poetry self add poetry-plugin-export
```

Then:

```bash
poetry export -f requirements.txt --output requirements.txt --without-hashes
```

## Testing

### Locust (performance)

1. Start the API:

```bash
poetry run uvicorn src.main:app --reload
```

2. **Web UI** (interactive):

```bash
poetry run locust -f tests/performance/locustfile.py --host http://127.0.0.1:8000
```

3. **Headless** (terminal statistics; adjust users, spawn rate, and duration):

```bash
poetry run locust -f tests/performance/locustfile.py --host http://127.0.0.1:8000 --headless -u 20 -r 5 -t 60s --only-summary
```

Optional environment variables for the scenario:

- `LOCUST_USER_ID` — default `1` if you skip seeding and know a valid user id.
- `LOCUST_USERNAME` — fixed username for `GET /users/search` (default: auto-generated per user).

The load script documents the Quality Plan performance target (**P95 under 200 ms**); check the printed percentile column after the run.

### Other utilities

```bash
poetry run pytest -q
poetry run flake8 src
poetry run pytest --cov=src --cov-fail-under=60
poetry run bandit -r src
poetry run radon cc -a -s src
poetry run radon mi -s src
```

## Quality Control

### Tests and coverage

`pyproject.toml` configures pytest with `--cov=src` and a **60%** coverage floor (`--cov-fail-under=60` and `[tool.coverage.report] fail_under`).

```bash
poetry run pytest
poetry run pytest --cov=src --cov-report=term-missing
```

### Static analysis and metrics

```bash
poetry run flake8 src tests streamlit_app.py
poetry run bandit -r src -c .bandit -lll
poetry run radon cc -a -s src/
poetry run radon mi -s src/
```

`.flake8` sets `max-complexity = 9` so Flake8 (McCabe) enforces **cyclomatic complexity strictly below 10** on most Python files; `streamlit_app.py` ignores `C901` because UI layout inflates branch counts while remaining readable. CI still runs a Radon JSON check so every block under **`src/`** stays **below 10**.

On every push and pull request, GitHub Actions (`.github/workflows/ci.yml`) installs dependencies with Poetry and runs **flake8**, **bandit** (high severity only), **pytest** with **at least 60%** coverage, and **radon** with cyclomatic complexity **below 10** for code under `src/`.

### Pre-commit

```bash
poetry run pre-commit install
poetry run pre-commit run --all-files
```
