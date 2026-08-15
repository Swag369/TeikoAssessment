PYTHON := python3

.PHONY: setup pipeline dashboard

setup:
	$(PYTHON) -m pip install -r requirements.txt

pipeline:
	$(PYTHON) load_data.py
	$(PYTHON) part2.py
	$(PYTHON) part3.py
	$(PYTHON) part4.py

dashboard:
	$(PYTHON) -m streamlit run streamlit_app.py
