import pandas as pd
import json
from sqlalchemy import create_engine, text

# PostgreSQL connection setup
DB_USER = 'kritsadakruapat'
DB_PASS = 'NewSecurePassword123!'
DB_HOST = 'localhost'
DB_PORT = '5432'
DB_NAME = 'revenue_dashboard'

engine = create_engine(
    f'postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
)

# Load FX rates from Kafka consumer output
FX_JSON_PATH = "fx_rate_data/fx_rates_kafka.json"

try:
    with open(FX_JSON_PATH, 'r') as f:
        fx_rates = json.load(f)
    print("Loaded FX rates from fx_rates_kafka.json.")
except Exception as e:
    print("Error reading FX rates:", e)
    fx_rates = {}

# Fetch the last 24 hours of transaction data
query = """
SELECT * FROM transactions
WHERE timestamp >= NOW() - INTERVAL '24 hours';
"""
df = pd.read_sql(query, engine)

# Convert to USD using latest FX rates
def convert(row):
    currency = row['currency']
    fx = fx_rates.get(currency, 1.0)
    return round(row['amount'] * fx, 2)

df['usd_converted'] = df.apply(convert, axis=1)

# Save to new table: transactions_converted
with engine.begin() as conn:
    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS transactions_converted (
            id SERIAL PRIMARY KEY,
            timestamp TIMESTAMP,
            user_id VARCHAR(50),
            country VARCHAR(10),
            currency VARCHAR(10),
            amount FLOAT,
            usd_converted FLOAT
        );
    """))

    conn.execute(text("""
        DELETE FROM transactions_converted
        WHERE timestamp >= NOW() - INTERVAL '24 hours';
    """))

    df_to_save = df[['timestamp', 'user_id', 'country', 'currency', 'amount', 'usd_converted']]
    df_to_save.to_sql('transactions_converted', engine, if_exists='append', index=False)
    print(f"Saved {len(df_to_save)} rows to 'transactions_converted' table.")

# Display a quick preview
print(df[['timestamp', 'currency', 'amount', 'usd_converted']].head())

