import sqlite3
import pandas as pd
import os
from scripts.extract_trades import load_client_orders, load_broker_trades
from scripts.reconcile_trades import reconcile_trades
from scripts.generate_reports import generate_reports
from scripts.email_fetcher import fetch_emails
from config.settings import DB_PATH, EMAIL_FOLDER

# Define data directories
REPORTS_DIR = "reports/"
LOGS_DIR = "logs/"

def main():
    """Execute full reconciliation process."""
    print("🔄 Starting trade reconciliation process...")

    # Ensure required directories exist
    os.makedirs(EMAIL_FOLDER, exist_ok=True)
    os.makedirs(REPORTS_DIR, exist_ok=True)
    os.makedirs(LOGS_DIR, exist_ok=True)

    # Load client orders
    print("📥 Loading client orders...")
    client_orders = load_client_orders()

    # Load broker trades from available data
    print("📥 Loading broker trades from available files...")
    load_broker_trades()

    # Run trade reconciliation
    print("⚖️ Running trade reconciliation...")
    reconcile_trades()

    # Generate final reports
    print("📊 Generating reports...")
    generate_reports()

    print("✅ Trade reconciliation process completed.")

if __name__ == "__main__":
    main()
