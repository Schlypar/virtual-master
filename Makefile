.PHONY: all docs clean help

all: docs

docs:
	@$(MAKE) -C docs all

clean:
	@$(MAKE) -C docs clean

help:
	@echo "Available targets:"
	@echo "  all   - Run all targets"
	@echo "  docs  - Generate docs"
	@echo "  clean - Remove generated items"