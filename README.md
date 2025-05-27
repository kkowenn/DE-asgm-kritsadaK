# Real-Time Revenue Dashboard (Data Engineering Project)

A mini data engineering pipeline that streams FX rates via Kafka, stores transactions in PostgreSQL, converts them to USD, and visualizes insights with Streamlit.

## Components Overview

| Script                             | Description                                                                           |
| ---------------------------------- | ------------------------------------------------------------------------------------- |
| `1_setup_postgres_transactions.py` | Generates and inserts transaction data into PostgreSQL using API FX rates             |
| `2_fx_rate_producer.py`            | Simulates FX rate streaming via Kafka                                                 |
| `3_fx_rate_consumer.py`            | Listens to Kafka and saves FX rates to local JSON                                     |
| `5_convert_fx_live.py`             | Converts transaction amounts to USD using latest FX from JSON                         |
| `4_streamlit_dashboard.py`         | Displays real-time revenue insights in Streamlit using `transactions_converted` table |

---

##  How to Run the Project manually using Python scripts.

### 0. Install Dependencies

```bash
pip install -r requirements.txt
```

### 1. Start Kafka

```bash
kafka-topics --list --bootstrap-server localhost:9092
```

### 2. Simulate Transactions

```bash
python 1_setup_postgres_transactions.py
```

### 3. Stream FX Rates

```bash
python 2_fx_rate_producer.py

# In another terminal

python 3_fx_rate_consumer.py
```

### 4. Convert to USD

```bash
python 4_convert_fx_live.py
```

### 5. Launch Dashboard

```bash
streamlit run 5_streamlit_dashboard.py
```

--- 

## PostgreSQL Tables

```bash
revenue_dashboard=# \dt
                     List of relations
 Schema |          Name          | Type  |      Owner      
--------+------------------------+-------+-----------------
 public | transactions           | table | kritsadakruapat
 public | transactions_converted | table | kritsadakruapat

```

## How to Run the Project Automaicalluy

You can run the project with **Docker Compose** 

---

###  Run with Docker 

> Automatically runs PostgreSQL, Kafka, Streamlit app, and Python scripts

### 1. Build and launch services:

```bash
./run_all.sh