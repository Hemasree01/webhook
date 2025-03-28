from flask import Flask, request, jsonify
from google.cloud import spanner

app = Flask(__name__)
spanner_client = spanner.Client()
instance = spanner_client.instance("bank-customer-instance")
database = instance.database("bank-customer-db")

@app.route('/query_customer', methods=['POST'])
def query_customer():
    req = request.get_json()
    customer_id = req.get("customer_id")
    pin = req.get("pin")

    query = """
    SELECT c.first_name, c.last_name, c.email, c.phone, a.account_id, a.account_type, a.balance, a.currency
    FROM customers c
    JOIN accounts a ON c.customer_id = a.customer_id
    WHERE c.customer_id = @customer_id AND c.pin = @pin;
    """
    params = {"customer_id": customer_id, "pin": pin}
    
    with database.snapshot() as snapshot:
        results = snapshot.execute_sql(query, params=params)
        data = [dict(zip(["first_name", "last_name", "email", "phone", "account_id", "account_type", "balance", "currency"], row)) for row in results]
    
    return jsonify({"customer_details": data})

if __name__ == '__main__':
    app.run(port=8080)
