unit:
	pytest -v

coverage:
	pytest --cov=crispy_models --cov-report=html --cov-report=term-missing


lint:
	flake8 crispy_models --count --select=E9,F63,F7,F82 --show-source --statistics
	flake8 crispy_models --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics
	mypy crispy_models
