import pandas as pd
import numpy as np
import requests
from datetime import datetime, timedelta
from sqlalchemy import create_engine, text

# === Step 1: PostgreSQL connection details ===
DB_USER = 'kritsadakruapat'
DB_PASS = 'NewSecurePassword123!'
DB_HOST = 'localhost'
DB_PORT = '5432'
DB_NAME = 'revenue_dashboard'

engine = create_engine(
    f'postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
)

# === Step 2: Create the transactions table ===
create_table_sql = """
CREATE TABLE IF NOT EXISTS transactions (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL,
    user_id VARCHAR(50),
    country VARCHAR(10),
    currency VARCHAR(10),
    amount FLOAT,
    usd_amount FLOAT
);
"""

# === Step 3: Get live FX rates from API ===
def get_live_fx_rates(base_currency='USD'):
    url = f'https://api.frankfurter.app/latest?from={base_currency}'
    response = requests.get(url)
    data = response.json()
    return data['rates']  # returns a dict like {'EUR': 0.92, 'JPY': 157.2, ...}

# === Step 4: Simulate transactions using live FX rates ===
def generate_transaction_data(n=10):
    users = ['user_' + str(i) for i in range(1, 11)]
    countries = ['US', 'UK', 'DE', 'FR', 'JP', 'AU', 'CA', 'IN', 'BR', 'SG']
    currencies = ['USD', 'GBP', 'EUR', 'EUR', 'JPY', 'AUD', 'CAD', 'INR', 'BRL', 'SGD']
    currency_map = dict(zip(countries, currencies))

    api_rates = get_live_fx_rates('USD')
    fx_rates = {k: 1 / v if v != 0 else 1 for k, v in api_rates.items()}  # to get USD per unit

    data = []
    for _ in range(n):
        country = np.random.choice(countries)
        user = np.random.choice(users)
        timestamp = datetime.now() - timedelta(hours=np.random.randint(0, 24))
        amount = np.random.uniform(10, 100)
        currency = currency_map[country]
        rate = fx_rates.get(currency, 1.0)  # fallback if currency missing
        usd_amount = amount * rate
        data.append({
            'timestamp': timestamp,
            'user_id': user,
            'country': country,
            'currency': currency,
            'amount': round(amount, 2),
            'usd_amount': round(usd_amount, 2),
        })

    return pd.DataFrame(data)

# === Step 5: Create and insert ===
df = generate_transaction_data()
print("\n Simulated Data:")
print(df.head())

with engine.begin() as conn:
    conn.execute(text(create_table_sql))
    df.to_sql('transactions', con=conn, if_exists='append', index=False)
    print(f"\n Inserted {len(df)} rows into 'transactions' table.")

# === Step 6: Query hourly data ===
query = """
SELECT * FROM transactions
WHERE timestamp >= NOW() - INTERVAL '1 hour'
ORDER BY timestamp DESC;
"""
df_hourly = pd.read_sql(query, engine)
print("\n Hourly Transactions (Last 1 Hour):")
print(df_hourly)
