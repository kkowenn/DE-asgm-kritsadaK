#  How to Run the Project

### 1. Start Kafka & Zookeeper

Make sure Kafka and Zookeeper are running via Homebrew:

```bash
brew services start zookeeper
brew services start kafka
```

### 2. Run FX Rate Streaming

```bash
python 2_fx_rate_producer.py    # Simulates live FX rate updates
python 3_fx_rate_consumer.py    # Saves FX data to fx_rate_data/fx_rates_kafka.json
```

### 3. Simulate Transactions

```bash
python 1_setup_postgres_transactions.py
```

This generates fake transactions and inserts them into PostgreSQL.

### 4. Convert to USD Using Real-Time FX

```bash
python 5_convert_fx_live.py
```

This recalculates USD using latest FX rates from Kafka and stores in a new table `transactions_converted`.

### 5. Launch the Dashboard

```bash
streamlit run 4_streamlit_dashboard.py
```

---

## What Each Script Does

| Script                             | Description                                                                           |
| ---------------------------------- | ------------------------------------------------------------------------------------- |
| `1_setup_postgres_transactions.py` | Generates and inserts transaction data into PostgreSQL using API FX rates             |
| `2_fx_rate_producer.py`            | Simulates FX rate streaming via Kafka                                                 |
| `3_fx_rate_consumer.py`            | Listens to Kafka and saves FX rates to local JSON                                     |
| `5_convert_fx_live.py`             | Converts transaction amounts to USD using latest FX from JSON                         |
| `4_streamlit_dashboard.py`         | Displays real-time revenue insights in Streamlit using `transactions_converted` table |

