MAKEFLAGS += --warn-undefined-variables
MAKEFLAGS += --no-builtin-rules

ARGS = $(filter-out $@, $(MAKECMDGOALS))

manage = uv run python manage.py
dirs = apps project_run

check: isort-check mypy ruff-check
format: isort-format ruff-format

run:
	@$(manage) runserver $(ARGS)

migrate:
	@$(manage) migrate $(ARGS)

ruff-check:
	@uv run ruff check $(dirs)

isort-check:
	@uv run isort --check $(dirs)

mypy:
	@uv run mypy $(dirs)

ruff-format:
	@uv run ruff format $(dirs)

isort-format:
	@uv run isort $(dirs)
