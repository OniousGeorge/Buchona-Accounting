"""Baseline test suite: untrained model on diverse transaction questions.

This script runs the untrained model against 15 transactions with 4 different
question types, capturing the baseline behavior before fine-tuning. Results are
saved with space for your ideal/expected answers, so we can measure improvement
after Days 3-5 fine-tuning.
"""
import db
from pipeline import run_pipeline
from datetime import datetime
from pathlib import Path
from inference_baseline import query_ollama


def run_baseline_tests():
    """Load transactions and run all 4 test questions as batch queries."""
    # Load the CSV and fetch transactions
    run_pipeline("bank_statement_test.csv")
    all_transactions = db.list_transactions()

    # Use only the first 15 transactions for the baseline
    test_transactions = all_transactions[:15]

    # Build a formatted string of all transactions for batch queries
    transaction_text = "Transactions:\n"
    for i, txn in enumerate(test_transactions, 1):
        _, _, description, _, txn_type, amount, _ = txn
        transaction_text += f"{i}. [{txn_type}] {description} - ${amount}\n"

    # Question 1: Categorize all transactions
    q1_prompt = f"""{transaction_text}

For each transaction above, provide a short category (e.g., Groceries, Insurance, Dining, Utilities).
Format: "1. [category], 2. [category], ..." etc."""

    # Question 2: Based on categorizations, what's the biggest expense?
    q2_prompt = f"""{transaction_text}

Based on these transactions, what is my biggest single expense and what category is it?
Answer in one sentence."""

    # Question 3: What are the main spending categories?
    q3_prompt = f"""{transaction_text}

What are the main spending categories you see across these transactions?
List 3-5 categories."""

    # Question 4: Which category appears most frequently?
    q4_prompt = f"""{transaction_text}

Which spending category appears most frequently in these transactions?
Answer with just the category name."""

    # Run all questions
    print("Running baseline test suite on 15 transactions...\n")

    q1_response = query_ollama(q1_prompt)
    print("Q1: Categorize all transactions")
    print(f"Response: {q1_response}\n")

    q2_response = query_ollama(q2_prompt)
    print("Q2: What is my biggest expense?")
    print(f"Response: {q2_response}\n")

    q3_response = query_ollama(q3_prompt)
    print("Q3: What are the main spending categories?")
    print(f"Response: {q3_response}\n")

    q4_response = query_ollama(q4_prompt)
    print("Q4: Which category appears most frequently?")
    print(f"Response: {q4_response}\n")

    # Save results to file
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    reports_dir = Path("reports")
    reports_dir.mkdir(exist_ok=True)

    results_file = reports_dir / "baseline_test_results.txt"

    with open(results_file, "w") as f:
        f.write(f"Baseline Test Suite Results\n")
        f.write(f"Generated: {timestamp}\n")
        f.write(f"Model: smollm2:1.7b-instruct-q4_0 (untrained)\n")
        f.write(f"Transactions tested: 15\n")
        f.write("=" * 80 + "\n\n")

        f.write("TRANSACTIONS TESTED:\n")
        f.write(transaction_text)
        f.write("\n" + "=" * 80 + "\n\n")

        f.write("Q1: Categorize all transactions\n")
        f.write("MODEL BASELINE ANSWER:\n")
        f.write(q1_response + "\n")
        f.write("\nYOUR IDEAL/EXPECTED ANSWER:\n")
        f.write("should categorize transactions based of their descriptions not on payment methods\n\n")

        f.write("=" * 80 + "\n\n")

        f.write("Q2: What is my biggest expense?\n")
        f.write("MODEL BASELINE ANSWER:\n")
        f.write(q2_response + "\n")
        f.write("\nYOUR IDEAL/EXPECTED ANSWER:\n")
        f.write("A deposit does not count as an expense and the number generated is completely wrong smh\n\n")

        f.write("=" * 80 + "\n\n")

        f.write("Q3: What are the main spending categories?\n")
        f.write("MODEL BASELINE ANSWER:\n")
        f.write(q3_response + "\n")
        f.write("\nYOUR IDEAL/EXPECTED ANSWER:\n")
        f.write("shopping is undoubtedly the largest category not gas\n\n")

        f.write("=" * 80 + "\n\n")

        f.write("Q4: Which category appears most frequently?\n")
        f.write("MODEL BASELINE ANSWER:\n")
        f.write(q4_response + "\n")
        f.write("\nYOUR IDEAL/EXPECTED ANSWER:\n")
        f.write("payment type should not be a category\n\n")

    print(f"Results saved to {results_file}")
    print("Fill in your ideal answers to establish goals for Days 3-5 fine-tuning.")


if __name__ == "__main__":
    run_baseline_tests()
