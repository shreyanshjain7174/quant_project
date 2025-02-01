import sqlite3
import pandas as pd
import email
import os
from email import policy
from email.parser import BytesParser


def load_client_orders(db_path="trades.db"):
    conn = sqlite3.connect(db_path)
    query = "SELECT * FROM UCC"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df


def parse_eml(eml_directory):
    broker_trades = []
    for filename in os.listdir(eml_directory):
        if filename.endswith(".eml"):
            with open(os.path.join(eml_directory, filename), "rb") as f:
                msg = BytesParser(policy=policy.default).parse(f)
                for part in msg.walk():
                    if (
                        part.get_content_type()
                        == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    ):
                        xlsx = part.get_payload(decode=True)
                        df = pd.read_excel(xlsx, engine="openpyxl")
                        broker_trades.append(df)
    if broker_trades:
        return pd.concat(broker_trades, ignore_index=True)
    return pd.DataFrame()


if __name__ == "__main__":
    client_orders = load_client_orders()
    broker_trades = parse_eml("eml_files")
    # Assume ISIN to symbol mapping (example)
    # broker_trades['symbol'] = broker_trades['Instrument ISIN'].map(isin_to_symbol)
    # For this example, assuming symbol is derived from ISIN (adjust as per actual mapping)
    broker_trades["symbol"] = broker_trades["Instrument ISIN"].str[:3]  # Placeholder
    broker_trades.to_sql(
        "broker_trades", sqlite3.connect("trades.db"), if_exists="replace", index=False
    )
    client_orders.to_sql(
        "client_orders", sqlite3.connect("trades.db"), if_exists="replace", index=False
    )
