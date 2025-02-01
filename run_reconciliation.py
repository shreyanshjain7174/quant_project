from extract_trades import load_client_orders, parse_eml
from reconcile_trades import reconcile_trades
from generate_reports import generate_reports
import sqlite3


def main():
    # Extract data
    client_orders = load_client_orders()
    broker_trades = parse_eml("eml_files")
    # Reconcile trades
    reconcile_trades()
    # Generate reports
    generate_reports()


if __name__ == "__main__":
    main()
