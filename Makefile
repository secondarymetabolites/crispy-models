unit:
	pytest -v

coverage:
	pytest --cov=crispy_models --cov-report=html --cov-report=term-missing
