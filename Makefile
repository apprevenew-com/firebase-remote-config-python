lint:
	ruff check . --fix

test:
	pytest . --disable-warnings -s
