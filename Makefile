.PHONY: compare catalog ai graphify graphify-deep

compare:
	python3 scripts/compare_all_upstream_official.py
	python3 scripts/compare_sozler.py
	python3 scripts/compare_sozler_official.py
	python3 scripts/compare_mektubat_official.py

catalog:
	python3 scripts/build_catalog.py

ai:
	python3 scripts/build_ai_corpus.py

graphify:
	graphify . --no-viz

graphify-deep:
	graphify . --mode deep --no-viz
