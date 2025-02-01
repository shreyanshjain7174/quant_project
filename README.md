# Advanced Trade Reconciliation & Data Processing System

## Overview
This project implements a **Python-based trade reconciliation system** that:
- Ingests **client orders** from an SQLite database (`trades.db`).
- Processes **trade execution files** from brokers (stored as `.eml` files with Excel attachments).
- Reconciles trades by matching **Ticker, ISIN, and Quantity**.
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
The database consists of the following table:
1. **trades**:
   | Column      | Type       | Description |
   |------------|-----------|-------------|
   | UCC        | TEXT      | Unique Client Code |
   | Ticker     | TEXT      | Stock Ticker |
   | ISIN       | TEXT      | Instrument ISIN |
   | Direction  | TEXT      | Buy/Sell Flag |
   | Quantity   | INTEGER   | Order Quantity |

## Execution
### Step 1: Extract and Parse Data
```bash
python extract_trades.py
```
- Reads **client orders** from `trades.db` (now the `trades` table).
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
  execution_slippage = (Net Amount / Quantity)
  ```

## Installation & Setup for FastApi branch
### 1️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```

### 2️⃣ Set Up Configuration
Modify `config/settings.py` with your email credentials and database details.

### 3️⃣ Run the Flask API
Start the Flask server to enable live execution:
```bash
python app.py
```

### 4️⃣ Trigger Trade Reconciliation via API
Use `curl` or Postman to trigger reconciliation on demand:
```bash
curl -X POST http://localhost:4000/run_reconciliation
```

### 5️⃣ Verify Reports
After execution, reports will be generated in the `reports/` directory:
```bash
ls -lh reports/
```

### 6️⃣ Check Flask API Logs
Logs will be stored in the `logs/` directory:
```bash
tail -f logs/flask_api.log
```

## Running the Full Workflow Manually
If you want to execute the full trade reconciliation process without the API:
```bash
python scripts/run_reconciliation.py
```