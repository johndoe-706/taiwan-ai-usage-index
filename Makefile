.PHONY: init test report figures

init:
	python3 -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt

test:
	pytest -q

figures:
	python -m src.viz.figures

report:
	python -m src.report.make_report
