.PHONY: setup setup-optional compare catalog ai audit-public verify-public graphify graphify-deep graphify-tree

GRAPHIFY_PATH ?= books/sozler
GRAPHIFY_BACKEND ?=
GRAPHIFY_MODEL ?=

GRAPHIFY_ARGS = extract $(GRAPHIFY_PATH) --out .
ifneq ($(strip $(GRAPHIFY_BACKEND)),)
GRAPHIFY_ARGS += --backend $(GRAPHIFY_BACKEND)
endif
ifneq ($(strip $(GRAPHIFY_MODEL)),)
GRAPHIFY_ARGS += --model $(GRAPHIFY_MODEL)
endif

setup:
	python3 -m pip install -r requirements.txt

setup-optional: setup
	python3 -m pip install -r requirements-optional.txt

compare:
	python3 scripts/compare_all_upstream_official.py
	python3 scripts/compare_sozler.py
	python3 scripts/compare_sozler_official.py
	python3 scripts/compare_mektubat_official.py

catalog:
	python3 scripts/build_catalog.py

ai:
	python3 scripts/build_ai_corpus.py

audit-public:
	python3 scripts/audit_public_repo.py

verify-public: catalog ai audit-public

graphify:
	./scripts/run_graphify.sh $(GRAPHIFY_ARGS)

graphify-deep:
	./scripts/run_graphify.sh $(GRAPHIFY_ARGS) --token-budget 90000 --max-concurrency 1

graphify-tree:
	./scripts/run_graphify.sh tree --graph graphify-out/graph.json --root $(GRAPHIFY_PATH) --label "$(GRAPHIFY_PATH)"
