MANAGE_PY = ./sample_proj/manage.py

.PHONY: test
test:
	$(MANAGE_PY) test datafilters polls
