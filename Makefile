
init:
	python -m venv venv
	. venv/bin/activate
	pip install -r requirements.txt

test:
	python src/.test_*.py

eval: 
	python src/.eval_*.py
clean: 
	rm -rf venv/
	find . | grep -E "(__pycache__|\.pyc|\.pyo)" | xargs rm -rf
