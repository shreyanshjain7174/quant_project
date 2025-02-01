import logging
import subprocess
from flask import Flask, request, jsonify
import os

# Setup logging
LOG_DIR = "logs/"
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, "flask_api.log")
logging.basicConfig(
    filename=LOG_FILE,
    filemode='a',
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

Flask.name = "trade-reconciliation-api"
app = Flask(__name__)

@app.route("/run_reconciliation", methods=['POST'])
def run_reconciliation():
    """Trigger the trade reconciliation process via API."""
    try:
        logging.info("API request received: Running trade reconciliation...")
        subprocess.Popen(["python", "scripts/run_reconciliation.py"])
        logging.info("Trade reconciliation completed successfully.")
        return jsonify({"status": "success", "message": "Reconciliation completed successfully."})
    except subprocess.CalledProcessError as e:
        logging.error(f"Error during reconciliation: {str(e)}")
        return jsonify({"status": "error", "message": str(e)})
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        return jsonify({"status": "error", "message": "An unexpected error occurred."})

if __name__ == "__main__":
    logging.info("Starting Flask API for trade reconciliation...")
    app.run(host="0.0.0.0", port=4000, debug=True)
