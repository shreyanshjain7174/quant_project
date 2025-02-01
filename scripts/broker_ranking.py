import sqlite3
import pandas as pd
from config.settings import DB_PATH 

def rank_brokers():
    """Rank brokers based on execution quality."""
    conn = sqlite3.connect(DB_PATH)

    # Calculate broker performance
    query = """
        SELECT 
            `party code/SEBI regn code of party` AS broker, 
            SUM(allocated_qty) AS total_filled,
            SUM(allocated_brokerage) AS total_brokerage,
            SUM(allocated_stt) AS total_stt
        FROM reconciliation_results
        GROUP BY broker
        ORDER BY total_filled DESC
    """
    
    df_broker_rank = pd.read_sql_query(query, conn)
    conn.close()

    # Compute ranking score (higher fill rate, lower cost is better)
    df_broker_rank["score"] = df_broker_rank["total_filled"] / (df_broker_rank["total_brokerage"] + df_broker_rank["total_stt"] + 1e-9)
    df_broker_rank.sort_values(by="score", ascending=False, inplace=True)

    # route to report generator
    return df_broker_rank

if __name__ == "__main__":
    rank_brokers()
