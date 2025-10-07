setup:
	python3 -m venv venv
	./venv/bin/pip install -r requirements.txt
run:
	./venv/bin/python bash.py
run-tcp:
	./venv/bin/python bash.py --tcp
