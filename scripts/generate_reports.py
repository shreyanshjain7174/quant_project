import pandas as pd
import sqlite3
from broker_ranking import rank_brokers
from config.settings import DB_PATH
import logging

def table_exists(conn, table_name):
    """Check if a table exists in the database."""
    query = f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}';"
    return pd.read_sql_query(query, conn).shape[0] == 1

def generate_reports():
    """Generate trade reconciliation reports."""
    conn = sqlite3.connect(DB_PATH)

    # Load matched trades
    try:
        matched = pd.read_sql_query("SELECT * FROM reconciliation_results", conn)
    except Exception as e:
        logging.info("⚠️ No matched trades found:", e)
        matched = pd.DataFrame()

    # Load unmatched trades
    if table_exists(conn, "unmatched_orders"):
        try:
            unmatched = pd.read_sql_query("SELECT * FROM unmatched_orders", conn)
        except Exception as e:
            logging.info("⚠️ No unmatched trades found:", e)
            unmatched = pd.DataFrame()
    else:
        logging.info("⚠️ No unmatched trades table found.")
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
        logging.info("⚠️ No broker summary data found:", e)
        broker_summary = pd.DataFrame()

    conn.close()

    # Save reports only if data exists
    if not matched.empty:
        matched.to_csv('reports/matched_trades.csv', index=False)
        logging.info("✅ Matched trades report generated.")

    if not unmatched.empty:
        unmatched.to_csv('reports/unmatched_trades.csv', index=False)
        logging.info("✅ Unmatched trades report generated.")

    if not broker_summary.empty:
        broker_summary.to_csv('reports/broker_summary.csv', index=False)
        logging.info("✅ Broker summary report generated.")
    
    rank_broker = rank_brokers()
    if not rank_broker.empty:
        rank_broker.to_csv('reports/broker_ranking.csv', index=False)
        logging.info("✅ Broker ranking report generated.") 

if __name__ == "__main__":
    generate_reports()
