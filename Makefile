MAKEFLAGS += --warn-undefined-variables
MAKEFLAGS += --no-builtin-rules

ARGS = $(filter-out $@, $(MAKECMDGOALS))

manage = uv run python manage.py

run:
	@$(manage) runserver $(ARGS)

migrate:
	@$(manage) migrate $(ARGS)
