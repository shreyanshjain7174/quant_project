import sqlite3
import pandas as pd
import logging
from config.settings import DB_PATH

def reconcile_trades(db_path = DB_PATH):
    """Reconcile broker trades with client orders and ensure tables exist."""
    conn = sqlite3.connect(db_path)

    # Load client orders
    client_orders = pd.read_sql_query("SELECT * FROM trades", conn)
    
    try:
        broker_trades = pd.read_sql_query("SELECT * FROM broker_trades", conn)
    except Exception as e:
        logging.info("⚠️ No broker trades found:", e)
        broker_trades = pd.DataFrame()

    conn.close()

    matched = []
    unmatched_orders = []
    broker_excess = []

    if not broker_trades.empty:
        broker_trades['Direction'] = broker_trades['Direction'].replace({'B': 'Buy', 'S': 'Sell'})

        for _, order in client_orders.iterrows():
            isin, direction, req_qty = order['ISIN'], order['Direction'], order['Quantity']

            relevant_trades = broker_trades[
                (broker_trades['Instrument ISIN'].str.strip() == isin.strip()) &
                (broker_trades['Direction'] == direction)
            ].copy()

            if relevant_trades.empty:
                unmatched_orders.append(order.to_dict())
                continue

            total_broker_qty = relevant_trades['QTY'].sum()

            if total_broker_qty >= req_qty:
                ratio = req_qty / total_broker_qty
                relevant_trades['allocated_qty'] = relevant_trades['QTY'] * ratio
                relevant_trades['allocated_brokerage'] = relevant_trades['Brokerage Amount'] * ratio
                relevant_trades['allocated_stt'] = relevant_trades['STT'] * ratio
                matched.extend(relevant_trades.to_dict('records'))
                
                excess = total_broker_qty - req_qty
                if excess > 0:
                    broker_excess.append({'ISIN': isin, 'excess': excess})
            else:
                relevant_trades['allocated_qty'] = relevant_trades['QTY']
                relevant_trades['allocated_brokerage'] = relevant_trades['Brokerage Amount']
                relevant_trades['allocated_stt'] = relevant_trades['STT']
                matched.extend(relevant_trades.to_dict('records'))
                unmatched_orders.append({**order.to_dict(), 'pending': req_qty - total_broker_qty})

    # Save results to database
    conn = sqlite3.connect(db_path)
    try:
        logging.info("Matched DataFrame:")
        # print(pd.DataFrame(matched))
        pd.DataFrame(matched).to_sql("reconciliation_results", conn, if_exists="replace", index=False)
    except sqlite3.OperationalError as e:
        logging.info(f"Error inserting matched: {e}")

    try:
        logging.info("Unmatched Orders DataFrame:")
        # print(pd.DataFrame(unmatched_orders))
        if unmatched_orders:
            df_unmatched = pd.DataFrame(unmatched_orders)
            if not df_unmatched.empty:
                logging.info("\n🔍 Unmatched Orders Data Preview:\n", df_unmatched.head())
                df_unmatched.to_sql("unmatched_orders", conn, if_exists="replace", index=False)
            else:
                logging.info("✅ No unmatched orders to insert, skipping table creation.")
        else:
            logging.info("✅ No unmatched orders to insert, skipping table creation.")
    except sqlite3.OperationalError as e:
        logging.info(f"Error inserting unmatched_orders: {e}")

    try:
        logging.info("Broker Excess DataFrame:")
        logging.info(pd.DataFrame(broker_excess))
        pd.DataFrame(broker_excess).to_sql("broker_excess", conn, if_exists="replace", index=False)
    except sqlite3.OperationalError as e:
        logging.info(f"Error inserting broker_excess: {e}")

    conn.close()

    logging.info(
        f"✅ Reconciliation complete. Matched: {len(matched)}, Unmatched: {len(unmatched_orders)}, Excess: {len(broker_excess)}"
    )

    return matched, unmatched_orders, broker_excess

if __name__ == "__main__":
    reconcile_trades()
