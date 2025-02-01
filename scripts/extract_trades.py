import sqlite3
import pandas as pd
import os
from scripts.email_fetcher import fetch_emails
from config.settings import EMAIL_FOLDER, DB_PATH
import logging

def load_client_orders(db_path=DB_PATH):
    """Load client orders from the trades table."""
    conn = sqlite3.connect(db_path)
    query = "SELECT * FROM trades"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def load_broker_trades(db_path=DB_PATH, trade_files=None):
    """Load broker trades from available trade files into broker_trades table."""
    broker_trades = []
    
    # Fetch latest broker trades from email
    fetch_emails()
    
    if trade_files is None:
        files_in_directory = os.listdir(EMAIL_FOLDER)
        trade_files = [f"{EMAIL_FOLDER}{file}" for file in files_in_directory if file.endswith((".xlsx", ".xls", ".csv"))]
    
    for file in trade_files:
        xls = pd.ExcelFile(file)
        for sheet in xls.sheet_names:
            df = xls.parse(sheet)

            # Standardize column names
            df.rename(columns={"Buy/Sell Flag": "Direction"}, inplace=True)
            df["Direction"] = df["Direction"].replace({"B": "Buy", "S": "Sell"})  # Convert B/S to Buy/Sell
            
            expected_columns = [
                "Deal Date", "party code/SEBI regn code of party", "Instrument ISIN",
                "Direction", "QTY", "COST", "NET AMOUNT", "Brokerage Amount",
                "Settlement Date", "STT", "Exchange Code", "Depository Code"
            ]
            
            # Keep only required columns
            df = df[expected_columns]
            broker_trades.append(df)

    if broker_trades:
        broker_trades_df = pd.concat(broker_trades, ignore_index=True)
    else:
        broker_trades_df = pd.DataFrame()

    # Save to database
    conn = sqlite3.connect(db_path)
    broker_trades_df.to_sql("broker_trades", conn, if_exists="replace", index=False)
    conn.close()
    logging.info(f"✅ Broker trades loaded successfully: {len(broker_trades_df)} records.")

if __name__ == "__main__":
    load_broker_trades()