from kafka import KafkaProducer
import json
import time
from datetime import datetime
import random

producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

fx_rates_base = {
    'EUR': 1.10, 'GBP': 1.30, 'JPY': 0.007, 'AUD': 0.65,
    'CAD': 0.75, 'INR': 0.012, 'BRL': 0.19, 'SGD': 0.74
}

while True:
    for currency, base_rate in fx_rates_base.items():
        rate = round(base_rate * (1 + random.uniform(-0.01, 0.01)), 4)
        message = {
            'currency': currency,
            'rate': rate,
            'timestamp': datetime.utcnow().isoformat()
        }
        producer.send('fx_rates', value=message)
        print(f"Sent: {message}")
    time.sleep(5)
