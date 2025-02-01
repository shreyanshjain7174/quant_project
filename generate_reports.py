import pandas as pd
import sqlite3


def generate_reports():
    conn = sqlite3.connect("trades.db")
    matched = pd.read_sql_query("SELECT * FROM reconciliation_results", conn)
    unmatched = pd.read_sql_query("SELECT * FROM unmatched_orders", conn)
    broker_summary = pd.read_sql_query(
        """
        SELECT `Party Code/SEBI Regn Code` as broker, 
               SUM(allocated_qty) as total_qty,
               SUM(allocated_brokerage) as total_brokerage,
               SUM(allocated_stt) as total_stt
        FROM reconciliation_results
        GROUP BY broker
    """,
        conn,
    )
    conn.close()

    matched.to_csv("reports/matched_trades.csv", index=False)
    unmatched.to_csv("reports/unmatched_trades.csv", index=False)
    broker_summary.to_csv("reports/broker_summary.csv", index=False)
