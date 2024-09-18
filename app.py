from flask import Flask, request, jsonify, CORS

import json

app = Flask(__name__)
CORS(app)


# Reuse the summarize function with slight modifications for Flask
def summarize(inputJSON):
    # Write your code here
    data = json.loads(inputJSON)

    available_credit = data['creditLimit']
    events = data['events']
    payable_balance = 0
    pending_transactions = {}
    settled_transactions = {}

    for event in events:
        txn_id = event['txnId']
        amount = event.get('amount', 0)
        event_time = event['eventTime']

        if event['eventType'] == "TXN_AUTHED":
            available_credit -= amount
            pending_transactions[txn_id] = {
                "amount": amount,
                "initial_time": event_time,
                "finalized_time": "N/A"
            }

        elif event['eventType'] == "TXN_AUTH_CLEARED":
            available_credit += pending_transactions[txn_id]["amount"]
            pending_transactions.pop(txn_id)

        elif event['eventType'] == "TXN_SETTLED":
            payable_balance += amount
            available_credit += pending_transactions[txn_id]["amount"] - amount

            settled_transactions[txn_id] = pending_transactions.pop(txn_id)
            settled_transactions[txn_id]['amount'] = amount
            settled_transactions[txn_id]["finalized_time"] = event_time

        elif event['eventType'] == "PAYMENT_INITIATED":
            payable_balance += amount
            pending_transactions[txn_id] = {
                "amount": amount,  # this value is negative
                "initial_time": event_time,
                "finalized_time": "N/A"
            }

        elif event['eventType'] == "PAYMENT_CANCELED":
            payable_balance -= pending_transactions[txn_id]["amount"]
            pending_transactions.pop(txn_id)

        elif event['eventType'] == "PAYMENT_POSTED":
            available_credit += abs(pending_transactions[txn_id]["amount"])
            settled_transactions[txn_id] = pending_transactions.pop(txn_id)
            settled_transactions[txn_id]["finalized_time"] = event_time

    # Sort transactions as specified
    pending_transactions = sorted(pending_transactions.items(), key=lambda x: x[1]['initial_time'], reverse=True)
    settled_transactions = sorted(settled_transactions.items(), key=lambda x: x[1]['initial_time'], reverse=True)[:3]

    # Prepare result string
    result = []
    result.append(f"Available credit: ${available_credit}")
    result.append(f"Payable balance: ${payable_balance}")
    result.append("")
    result.append("Pending transactions:")

    for txn_id, values in pending_transactions:
        if values["amount"] < 0:
            result.append(f"{txn_id}: -${abs(values['amount'])} @ time {values['initial_time']}")
        else:
            result.append(f"{txn_id}: ${values['amount']} @ time {values['initial_time']}")

    result.append("")
    result.append("Settled transactions:")

    for txn_id, values in settled_transactions:
        if values["amount"] < 0:
            result.append(
                f"{txn_id}: -${abs(values['amount'])} @ time {values['initial_time']} (finalized @ time {values['finalized_time']})")
        else:
            result.append(
                f"{txn_id}: ${values['amount']} @ time {values['initial_time']} (finalized @ time {values['finalized_time']})")

    return "\n".join(result)

@app.route('/summary', methods=['GET'])
def get_summary():
    return "This route is not implemented yet. Please use the POST /summarize route."


# Route to accept JSON input for summarize
@app.route('/summarize', methods=['POST'])
def summarize_route():
    inputJSON = request.data.decode('utf-8')  # Get the JSON from the POST request
    result = summarize(inputJSON)  # Call the summarize function
    return result  # Return the result string as the response


if __name__ == '__main__':
    app.run(debug=True)
