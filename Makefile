lint:
	ruff check . --fix

test:
	pytest . -s
