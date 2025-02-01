import sqlite3
import pandas as pd
from datetime import datetime


def reconcile_trades():
    conn = sqlite3.connect("trades.db")
    client_orders = pd.read_sql_query("SELECT * FROM client_orders", conn)
    broker_trades = pd.read_sql_query("SELECT * FROM broker_trades", conn)
    conn.close()

    client_orders["order_date"] = pd.to_datetime(client_orders["order_date"])
    broker_trades["Deal Date"] = pd.to_datetime(
        broker_trades["Deal Date"], format="%m/%d/%y"
    )

    matched = []
    unmatched_orders = []
    broker_excess = []

    for _, order in client_orders.iterrows():
        symbol = order["symbol"]
        date = order["order_date"]
        req_qty = order["quantity"]

        relevant_trades = broker_trades[
            (broker_trades["symbol"] == symbol) & (broker_trades["Deal Date"] == date)
        ].copy()

        if relevant_trades.empty:
            unmatched_orders.append(order.to_dict())
            continue

        total_broker_qty = relevant_trades["Quantify"].sum()
        if total_broker_qty >= req_qty:
            ratio = req_qty / total_broker_qty
            relevant_trades["allocated_qty"] = relevant_trades["Quantify"] * ratio
            relevant_trades["allocated_brokerage"] = (
                relevant_trades["Brokers gg. Amount"] * ratio
            )
            relevant_trades["allocated_stt"] = relevant_trades["STT"] * ratio
            matched.extend(relevant_trades.to_dict("records"))
            excess = total_broker_qty - req_qty
            if excess > 0:
                broker_excess.append({"symbol": symbol, "date": date, "excess": excess})
        else:
            relevant_trades["allocated_qty"] = relevant_trades["Quantify"]
            relevant_trades["allocated_brokerage"] = relevant_trades[
                "Brokers gg. Amount"
            ]
            relevant_trades["allocated_stt"] = relevant_trades["STT"]
            matched.extend(relevant_trades.to_dict("records"))
            unmatched_orders.append(
                {**order.to_dict(), "pending": req_qty - total_broker_qty}
            )

    # Save to database
    conn = sqlite3.connect("trades.db")
    pd.DataFrame(matched).to_sql(
        "reconciliation_results", conn, if_exists="replace", index=False
    )
    pd.DataFrame(unmatched_orders).to_sql(
        "unmatched_orders", conn, if_exists="replace", index=False
    )
    pd.DataFrame(broker_excess).to_sql(
        "broker_excess", conn, if_exists="replace", index=False
    )
    conn.close()

    return matched, unmatched_orders, broker_excess
