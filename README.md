# Advanced Trade Reconciliation & Data Processing System

## Overview
This project implements a **Python-based trade reconciliation system** that:
- Ingests **client orders** from an SQLite database (`trades.db`).
- Processes **trade execution files** from brokers (stored as `.eml` files with Excel attachments).
- Reconciles trades by matching **symbol, date, and quantity**.
- Handles **partial matches, excess trades, and pending orders**.
- Computes brokerage, STT, and total trade costs.
- Stores results in **SQLite** and generates **CSV reports**.
- Supports **automatic execution via scheduling**.

## File Structure
```
project/
├── extract_trades.py        # Extracts client orders and broker trades
├── reconcile_trades.py      # Performs trade reconciliation
├── generate_reports.py      # Generates reconciliation reports
├── run_reconciliation.py    # Automates the workflow
├── trades.db                # SQLite database for storing trades
├── reports/                 # Stores generated reports
│   ├── matched_trades.csv
│   ├── unmatched_trades.csv
│   ├── broker_summary.csv
└── README.md                # Documentation (this file)
```

## Setup Instructions
### Prerequisites
Ensure you have the following installed:
- **Python 3.8+**
- **pip** (Python package manager)
- Required Python libraries:
  ```bash
  pip install pandas sqlite3 openpyxl
  ```

### Database Schema (`trades.db`)
The database consists of the following tables:
1. **client_orders**:
   | Column      | Type       | Description |
   |------------|-----------|-------------|
   | order_id   | TEXT       | Unique order identifier |
   | client_id  | TEXT       | Client identifier |
   | symbol     | TEXT       | Stock symbol |
   | quantity   | INTEGER    | Order quantity |
   | order_price| FLOAT      | Price per unit |
   | order_date | DATE       | Order placement date |

2. **broker_trades**:
   | Column                      | Type   | Description |
   |-----------------------------|--------|-------------|
   | Deal Date                   | DATE   | Execution date |
   | Party Code/SEBI Regn Code    | TEXT   | Broker code |
   | Instrument ISIN              | TEXT   | Security ISIN |
   | Buy/Sell Flag                | TEXT   | B for Buy, S for Sell |
   | Quantity                     | INTEGER | Executed quantity |
   | Cost                         | FLOAT  | Cost per unit |
   | Net Amount                   | FLOAT  | Total trade amount |
   | Brokerage Amount              | FLOAT  | Brokerage cost |
   | Settlement Date               | DATE   | Trade settlement date |
   | STT                          | FLOAT  | Securities Transaction Tax |
   | Exchange Code                 | TEXT   | Exchange identifier |
   | Depository Code               | TEXT   | Depository identifier |

3. **reconciliation_results**:
   Stores matched trades with allocated costs and quantity.

4. **unmatched_orders**:
   Stores client orders that couldn't be fulfilled by broker trades.

5. **broker_excess**:
   Tracks excess broker trades beyond client requirements.

## Execution
### Step 1: Extract and Parse Data
```bash
python extract_trades.py
```
- Reads **client orders** from `trades.db`.
- Extracts **trade execution files** from `.eml` attachments.
- Stores broker trades in `broker_trades` table.

### Step 2: Run Trade Reconciliation
```bash
python reconcile_trades.py
```
- Matches broker trades with client orders.
- Handles **exact matches, partial allocations, excess trades, and pending orders**.
- Stores results in `reconciliation_results`.

### Step 3: Generate Reports
```bash
python generate_reports.py
```
- Creates CSV reports:
  - `reports/matched_trades.csv`
  - `reports/unmatched_trades.csv`
  - `reports/broker_summary.csv`

### Step 4: Automate Execution
```bash
python run_reconciliation.py
```
Alternatively, schedule it:
- **Linux (Cron job)**:
  ```bash
  0 18 * * * python3 run_reconciliation.py
  ```
- **Windows (Task Scheduler)**:
  - Open Task Scheduler
  - Create New Task
  - Set trigger: Daily at 6 PM
  - Action: Start `python run_reconciliation.py`

## Reconciliation Logic
- **Exact Match**: If broker trade quantity exactly matches the client order, mark as matched.
- **Partial Match**: If broker trades **partially fill** an order, allocate proportionally.
- **Excess Quantity**: If broker executes more than required, track excess.
- **Unmatched Orders**: Orders that remain unfilled are flagged as pending.
- **Multiple Brokers**: Orders are allocated proportionally based on broker execution quantity.
- **Slippage Calculation**:
  ```python
  execution_slippage = order_price - (Net Amount / Quantity)
  ```

