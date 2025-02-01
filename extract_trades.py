import sqlite3
import pandas as pd
import os
import io  # Import BytesIO
from email import policy
from email.parser import BytesParser

def load_client_orders(db_path='trades.db'):
    """Load client orders from the trades table."""
    conn = sqlite3.connect(db_path)
    query = "SELECT * FROM trades"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def parse_eml(eml_directory='eml_files'):
    """Parse .eml files to extract broker trade details."""
    broker_trades = []
    for filename in os.listdir(eml_directory):
        if filename.endswith('.eml'):
            with open(os.path.join(eml_directory, filename), 'rb') as f:
                msg = BytesParser(policy=policy.default).parse(f)
                for part in msg.walk():
                    if part.get_content_type() == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet':
                        xlsx_bytes = part.get_payload(decode=True)
                        xlsx_io = io.BytesIO(xlsx_bytes)  # Wrap in BytesIO
                        
                        df = pd.read_excel(xlsx_io, engine='openpyxl')

                        expected_columns = [
                            "Deal Date", "party code/SEBI regn code of party", "Instrument ISIN",
                            "Buy/Sell Flag", "QTY", "COST", "NET AMOUNT", "Brokerage Amount",
                            "Settlement Date", "STT", "Exchange Code", "Depository Code"
                        ]
                        df = df[expected_columns]  # Exclude any extra columns
                        
                        broker_trades.append(df)

    return pd.concat(broker_trades, ignore_index=True) if broker_trades else pd.DataFrame()
