.PHONY: all install build-db run dashboard clean

setup:
	pip install -r requirements.txt

pipeline:
	python load_data.py

dashboard:
	streamlit run dashboard.py --server.port 8501 --server.address 0.0.0.0