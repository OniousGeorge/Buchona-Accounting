"""CSV-to-database ingestion pipeline.

Wires together the three pieces that previously only existed in isolation:
CSV parsing (originally csv.ipynb cell 1), normalize()/validate()
(validation.py), and create_transaction() (db.py). This is the fix for the
bug CLAUDE.md flags: the parse step was never actually connected to
validation or the database.
"""
import csv
from collections import Counter

import db
from validation import debit_normalize, debit_validate, credit_normalize, credit_validate

def print_report(report):
    print(f"Processed: {report['processed']}")
    print(f"Inserted:  {report['inserted']}")
    print(f"Duplicates skipped: {report['duplicates']}")
    print(f"Failures: {len(report['failures'])}")
    for row_number, reason in report["failures"]:
        print(f"  row {row_number}: {reason}")


def run_debit_pipeline(csv_path):
    """Read csv_path, validate each row, and insert valid rows into the database.

    Returns a report dict: {"processed", "inserted", "duplicates", "failures"},
    where "failures" is a list of (row_number, reason) tuples.
    """
    db.init_db()

    debit_report = {"processed": 0, "inserted": 0, "duplicates": 0, "failures": []}
    # Counts identical rows within this file so genuine repeats get occurrence 1, 2, ...
    seen = Counter()

    with open(csv_path, newline="") as f:
        reader = csv.DictReader(f)
        for row_number, row in enumerate(reader, start=1):
            debit_report["processed"] += 1

            statement = {
                "Description": row["Transaction Description"],
                "Date": row["Transaction Date"],
                "Amount": row["Transaction Amount"],
                "Balance": row["Balance"],
            }

            error = debit_normalize(statement)
            if error is not None:
                debit_report["failures"].append((row_number, error))
                continue
            if(row["Transaction Type"] == "Debit"):
                statement["Amount"]*=-1
            error = debit_validate(statement)
            if error is not None:
                debit_report["failures"].append((row_number, error))
                continue

            key = (statement["Description"], statement["Date"], statement["Amount"], statement["Balance"])
            seen[key] += 1
            statement["Occurrence"] = seen[key]

            result = db.create_debit_transaction(statement)
            if result is None:
                debit_report["duplicates"] += 1
            else:
                debit_report["inserted"] += 1

    return debit_report

def run_credit_pipeline(csv_path):
    """Read csv_path, validate each row, and insert valid rows into the database.

    Returns a report dict: {"processed", "inserted", "duplicates", "failures"},
    where "failures" is a list of (row_number, reason) tuples.
    """
    db.init_db()

    credit_report = {"processed": 0, "inserted": 0, "duplicates": 0, "failures": []}
    # Counts identical rows within this file so genuine repeats get occurrence 1, 2, ...
    seen = Counter()

    with open(csv_path, newline="") as f:
        reader = csv.DictReader(f)
        for row_number, row in enumerate(reader, start=1):
            credit_report["processed"] += 1

            statement = {
                "Description": row["Description"],
                "Date": row["Transaction Date"],
                "Amount": row["Debit"],
                "Category": row["Category"]
            }

            if statement["Amount"] == '':
                statement["Amount"]=row["Credit"]
            

            error = credit_normalize(statement)
            if error is not None:
                credit_report["failures"].append((row_number, error))
                continue
            if row["Credit"] == '':
                statement["Amount"]*=-1
            error = credit_validate(statement)
            if error is not None:
                credit_report["failures"].append((row_number, error))
                continue

            key = (statement["Description"], statement["Date"], statement["Amount"])
            seen[key] += 1
            statement["Occurrence"] = seen[key]

            result = db.create_credit_transaction(statement)
            if result is None:
                credit_report["duplicates"] += 1
            else:
                credit_report["inserted"] += 1

    return credit_report

if __name__ == "__main__":
    debit_report = run_debit_pipeline(db.DATA_DIR / "debit_statements.csv")
    credit_report = run_credit_pipeline(db.DATA_DIR / "credit_statements.csv")
    print("Debit Report:\n")
    print_report(debit_report)
    print("=" * 80)
    print("Credit Report:\n")
    print_report(credit_report)
    
