.PHONY: sync-resume check-site

sync-resume:
	./scripts/sync_resume.sh

check-site:
	python3 scripts/check_html.py
