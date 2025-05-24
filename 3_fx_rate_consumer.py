from kafka import KafkaConsumer
import json
import os

# Ensure output directory exists
os.makedirs("fx_rate_data", exist_ok=True)

# Set output file path
output_path = "fx_rate_data/fx_rates_kafka.json"

# Initialize Kafka Consumer
consumer = KafkaConsumer(
    'fx_rates',
    bootstrap_servers='localhost:9092',
    auto_offset_reset='latest',
    value_deserializer=lambda m: json.loads(m.decode('utf-8'))
)

fx_cache = {}

print("Listening for FX rate updates...")
for msg in consumer:
    data = msg.value
    currency = data['currency']
    rate = data['rate']
    fx_cache[currency] = rate
    print(f"Updated {currency}: {rate}")

    # Save updated cache to file
    with open(output_path, 'w') as f:
        json.dump(fx_cache, f, indent=2)
