## Contributors

| Name   | Mail                   | Telegram alias | Github nickname|
|-----------------|--------------------------|----------------|----------------|
| Danil Valiev | d.valiev@innopolis.university | @dorley  | Dorley174 |
| Egor Savchenko | e.savchenko@innopolis.university | @KOSMOGOR | KOSMOGOR |
| Valeria Kolesnikova| v.kolesnikova@innopolis.university | @Codekd | cdeth567 |
| Nikita Solomennikov | n.solomennikov@innopolis.university | @Hiksol | Hiksol |
| Bulat Shigapov | b.shigapov@innopolis.university | @blt326Ray | Ray3264 |

## Testing

### Locust

- Start an app with
```python
python -m uvicorn src.main:app --reload  
```

- In other terminal
```python
python -m locust -f .\locustfile.py --host http://127.0.0.1:8000
```


### Other utilities

```python
python -m pytest -q
python -m flake8 src
python -m pytest --cov=src --cov-fail-under=60
python -m bandit -r src
python -m radon cc -a -s src
python -m radon mi -s src
```

## Quality Control

### Run the app and demo

1. Create a virtual environment and install dependencies:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

On macOS or Linux, activate with `source .venv/bin/activate` instead of `.venv\Scripts\activate`.

2. Start the API (repository root):

```bash
python -m uvicorn src.main:app --reload
```

3. Streamlit demo (separate terminal):

```bash
streamlit run streamlit_app.py
```

### Tests and coverage

`pytest.ini` already sets `--cov=src` and a **60%** coverage floor:

```bash
pytest
pytest --cov=src
pytest --cov=src --cov-report=term-missing
```

### Static analysis and metrics

```bash
flake8 src tests streamlit_app.py
python -m flake8 src tests streamlit_app.py
bandit -r src -c .bandit -lll
python -m bandit -r src -c .bandit -lll
radon cc -a -s src/
python -m radon cc -a -s src/
python -m radon mi -s src/
```

On every push and pull request, GitHub Actions (`.github/workflows/ci.yml`) installs dependencies and runs **flake8**, **bandit** (high severity only), **pytest** with **≥ 60%** coverage, and **radon** with cyclomatic complexity **CC < 10** for code under `src/`.

### Pre-commit

```bash
pre-commit install
pre-commit run --all-files
```