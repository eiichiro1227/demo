init:
	sudo apt update
	sudo apt install python3 python3-dev python3-venv
	wget https://bootstrap.pypa.io/get-pip.py
	sudo python3 get-pip.py
	python3 -m venv env

venv:
	env/bin/activate && exec bash

install:
	pip install -r requirements.txt
