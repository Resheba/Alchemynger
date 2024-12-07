.SILENT:
.PHONY: init requirements run


init:
	POETRY_VIRTUALENVS_IN_PROJECT=true env -u VIRTUAL_ENV poetry install --no-root
	pre-commit install

requirements:
	poetry export -f requirements.txt -o requirements.txt --without-hashes --without-urls
	poetry export -f requirements.txt -o dev-requirements.txt --with=dev --without-hashes --without-urls
