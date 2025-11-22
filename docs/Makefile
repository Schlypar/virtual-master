PUML_FILES := $(shell find . -name "*.puml")
PNG_TARGETS := $(PUML_FILES:.puml=.png)

.PHONY: all clean help

all: $(PNG_TARGETS)
	@echo "✅ All diagrams generated"

%.png: %.puml
	@echo "Generating: $@"
	@mkdir -p $(dir $@)
	@docker run --rm -v "$(CURDIR):/data" plantuml/plantuml \
		-o "/data/$(dir $<)" \
		"/data/$<"

clean:
	@find . -name "*.png" -delete
	@echo "✅ Clean complete"

help:
	@echo "Available targets:"
	@echo "  all   - Generate all PNG diagrams"
	@echo "  clean - Remove generated diagrams"