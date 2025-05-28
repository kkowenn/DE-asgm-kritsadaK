#!/bin/bash

echo "Step 1: Starting Docker containers..."
docker compose up -d --build

echo "Waiting for services to be ready..."
sleep 10

echo "Step 2: Running data ingestion and stream processors..."

echo "Inserting sample transactions..."
docker exec -it revenue_dashboard_app python 1_setup_postgres_transactions.py

echo "Starting FX rate producer..."
docker exec -d revenue_dashboard_app python 2_fx_rate_producer.py

echo "Starting FX rate consumer..."
docker exec -d revenue_dashboard_app python 3_fx_rate_consumer.py

echo "Starting FX-to-USD converter..."
docker exec -d revenue_dashboard_app python 4_convert_fx_live.py

echo "All components are running."
echo "Open the dashboard at: http://localhost:8501"
