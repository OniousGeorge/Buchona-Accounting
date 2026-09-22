import requests
import db

from pipeline import run_pipeline


def query_ollama(prompt, temperature=1.0):

    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "smollm2:1.7b-instruct-q4_0",
            "prompt": prompt,
            "temperature": temperature,
            "stream": False,
        },
    )
    response.raise_for_status()
    return response.json()["response"]

if __name__ == "__main__":
    # Load transactions from the database
    run_pipeline("bank_statement_test.csv")
    transactions = db.list_transactions()

    # Test inference on the first 3 transactions
    for i, txn in enumerate(transactions[:15], 1):
        statement_id, acct, description, date, txn_type, amount, balance = txn

        prompt = f"""Categorize this bank transaction.
        Description: {description}
        Type: {txn_type}
        Amount: ${amount}

        Category (be concise):"""

        print(f"\n--- Transaction {i} ---")
        print(f"Description: {description}")
        print(f"Amount: ${amount}")

        response = query_ollama(prompt)
        print(f"Model's categorization: {response}")