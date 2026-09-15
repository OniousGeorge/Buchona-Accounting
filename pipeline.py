"""CSV-to-database ingestion pipeline.

Wires together the three pieces that previously only existed in isolation:
CSV parsing (originally csv.ipynb cell 1), normalize()/validate()
(validation.py), and create_transaction() (db.py). This is the fix for the
bug CLAUDE.md flags: the parse step was never actually connected to
validation or the database.
"""
import csv

import db
from validation import normalize, validate


def run_pipeline(csv_path):
    """Read csv_path, validate each row, and insert valid rows into the database.

    Returns a report dict: {"processed", "inserted", "duplicates", "failures"},
    where "failures" is a list of (row_number, reason) tuples.
    """
    db.init_db()

    report = {"processed": 0, "inserted": 0, "duplicates": 0, "failures": []}

    with open(csv_path, newline="") as f:
        reader = csv.DictReader(f)
        for row_number, row in enumerate(reader, start=1):
            report["processed"] += 1

            statement = {
                "Acct_NO": row["Account Number"],
                "Description": row["Transaction Description"],
                "Date": row["Transaction Date"],
                "Type": row["Transaction Type"],
                "Amount": row["Transaction Amount"],
                "Balance": row["Balance"],
            }

            error = normalize(statement)
            if error is not None:
                report["failures"].append((row_number, error))
                continue

            error = validate(statement)
            if error is not None:
                report["failures"].append((row_number, error))
                continue

            result = db.create_transaction(statement)
            if result is None:
                report["duplicates"] += 1
            else:
                report["inserted"] += 1

    return report


if __name__ == "__main__":
    report = run_pipeline("bank_statement_test.csv")
    print(f"Processed: {report['processed']}")
    print(f"Inserted:  {report['inserted']}")
    print(f"Duplicates skipped: {report['duplicates']}")
    print(f"Failures: {len(report['failures'])}")
    for row_number, reason in report["failures"]:
        print(f"  row {row_number}: {reason}")
