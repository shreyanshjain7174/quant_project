import pandas as pd
import sqlite3

def table_exists(conn, table_name):
    """Check if a table exists in the database."""
    query = f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}';"
    return pd.read_sql_query(query, conn).shape[0] == 1

def generate_reports():
    """Generate trade reconciliation reports."""
    conn = sqlite3.connect('trades.db')

    # Load matched trades
    try:
        matched = pd.read_sql_query("SELECT * FROM reconciliation_results", conn)
    except Exception as e:
        print("⚠️ No matched trades found:", e)
        matched = pd.DataFrame()

    # Load unmatched trades
    if table_exists(conn, "unmatched_orders"):
        try:
            unmatched = pd.read_sql_query("SELECT * FROM unmatched_orders", conn)
        except Exception as e:
            print("⚠️ No unmatched trades found:", e)
            unmatched = pd.DataFrame()
    else:
        print("⚠️ No unmatched trades table found.")
        unmatched = pd.DataFrame()

    # Broker summary report
    try:
        broker_summary = pd.read_sql_query("""
            SELECT `party code/SEBI regn code of party` AS broker, 
                   SUM(allocated_qty) AS total_qty,
                   SUM(allocated_brokerage) AS total_brokerage,
                   SUM(allocated_stt) AS total_stt
            FROM reconciliation_results
            GROUP BY broker
        """, conn)
    except Exception as e:
        print("⚠️ No broker summary data found:", e)
        broker_summary = pd.DataFrame()

    conn.close()

    # Save reports only if data exists
    if not matched.empty:
        matched.to_csv('reports/matched_trades.csv', index=False)
        print("✅ Matched trades report generated.")

    if not unmatched.empty:
        unmatched.to_csv('reports/unmatched_trades.csv', index=False)
        print("✅ Unmatched trades report generated.")

    if not broker_summary.empty:
        broker_summary.to_csv('reports/broker_summary.csv', index=False)
        print("✅ Broker summary report generated.")

if __name__ == "__main__":
    generate_reports()
