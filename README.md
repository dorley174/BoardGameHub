## Contributors

| Name   | Mail                   | Telegram alias | Github nickname|
|-----------------|--------------------------|----------------|----------------|
| Danil Valiev | d.valiev@innopolis.university | @dorley  | Dorley174 |
| Egor Savchenko | e.savchenko@innopolis.university | @KOSMOGOR | KOSMOGOR |
| Valeria Kolesnikova| v.kolesnikova@innopolis.university | @Codekd | cdeth567 |
| Nikita Solomennikov | n.solomennikov@innopolis.university | @Hiksol | Hiksol |
| Bulat Shigapov | b.shigapov@innopolis.university | @blt326Ray | Ray3264 |

## Testing

```python
python -m pytest -q
python -m flake8 src
python -m pytest --cov=src --cov-fail-under=60
python -m bandit -r src
python -m radon cc -a -s src
python -m radon mi -s src
```