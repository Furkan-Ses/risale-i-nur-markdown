.PHONY: setup setup-optional compare catalog ai audit-public verify-public graphify graphify-deep

GRAPHIFY_PATH ?= books/sozler

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
	graphify $(GRAPHIFY_PATH)

graphify-deep:
	graphify $(GRAPHIFY_PATH) --mode deep
