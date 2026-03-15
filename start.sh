#!/bin/bash
# wait for endee database to be ready
echo "Waiting 5 seconds for Endee to start..."
sleep 5

# run ingestion in the background
echo "Starting background ingestion of documents..."
(cd backend && python3 ingest.py) &

# start streamlit immediately
echo "Starting Streamlit..."
streamlit run streamlit_app.py --server.port=8501 --server.address=0.0.0.0
