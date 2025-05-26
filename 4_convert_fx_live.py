import pandas as pd
import json
from sqlalchemy import create_engine, text

# === Step 1: Load FX Rates ===
print("Step 1: Loading FX rates from JSON")
FX_JSON_PATH = "fx_rate_data/fx_rates_kafka.json"

try:
    with open(FX_JSON_PATH, 'r') as f:
        fx_rates = json.load(f)
    print("Step 1.1: FX rates loaded successfully")
except Exception as e:
    print("Step 1.2: Failed to load FX rates:", e)
    fx_rates = {}

# === Step 2: Connect to PostgreSQL ===
print("Step 2: Connecting to PostgreSQL")
DB_USER = 'kritsadakruapat'
DB_PASS = 'NewSecurePassword123!'
DB_HOST = 'localhost'
DB_PORT = '5432'
DB_NAME = 'revenue_dashboard'

engine = create_engine(f'postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}')
print("Step 2.1: Connected to database")

# === Step 3: Read Transactions ===
print("Step 3: Reading recent transactions from database")

query = """
SELECT * FROM transactions
WHERE timestamp >= (CURRENT_TIMESTAMP AT TIME ZONE 'Asia/Bangkok') - INTERVAL '24 hours';
"""

df = pd.read_sql(query, engine)
print(f"Step 3.1: Loaded {len(df)} transactions")
if df.empty:
    print("No recent transactions found. Exiting early.")
    exit(0)

# === Step 4: Convert to USD ===
print("Step 4: Converting amounts to USD")

def convert(row):
    fx = fx_rates.get(row['currency'], 1.0)
    return round(row['amount'] * fx, 2)

df['usd_converted'] = df.apply(convert, axis=1)
print("Step 4.1: FX conversion complete")

# === Step 5: UPSERT to transactions_converted ===
print("Step 5: Writing to transactions_converted table")

insert_query = """
INSERT INTO transactions_converted (timestamp, user_id, country, currency, amount, usd_converted)
VALUES (:timestamp, :user_id, :country, :currency, :amount, :usd_converted)
ON CONFLICT (user_id, timestamp)
DO UPDATE SET
    country = EXCLUDED.country,
    currency = EXCLUDED.currency,
    amount = EXCLUDED.amount,
    usd_converted = EXCLUDED.usd_converted;
"""

with engine.begin() as conn:
    print("Step 5.1: Creating table if it doesn't exist with primary key")
    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS transactions_converted (
            timestamp TIMESTAMP NOT NULL,
            user_id VARCHAR(50) NOT NULL,
            country VARCHAR(10),
            currency VARCHAR(10),
            amount FLOAT,
            usd_converted FLOAT,
            PRIMARY KEY (user_id, timestamp)
        );
    """))

    print("Step 5.2: Inserting or updating rows via UPSERT")
    for _, row in df.iterrows():
        conn.execute(text(insert_query), {
            'timestamp': row['timestamp'],
            'user_id': row['user_id'],
            'country': row['country'],
            'currency': row['currency'],
            'amount': row['amount'],
            'usd_converted': row['usd_converted']
        })

print(f"Step 5.3: Upserted {len(df)} rows successfully")
print("Step 6: Script completed successfully")
