"""Type coercion and validation for a single transaction dict.

Migrated from csv.ipynb. The original functions printed an error and
returned False on failure, so the reason a row failed only ever reached the
console. These now return None on success, or an error message string
describing exactly what failed, so a caller (pipeline.py, later) can decide
what to do with that message instead of it being forced to stdout.
"""
from datetime import datetime


def normalize(statement):
    """Coerce fields to their expected types, in place.

    Returns None on success, or an error message string on failure.
    """
    if type(statement.get("Acct_NO")) != str:
        statement["Acct_NO"] = str(statement["Acct_NO"])
    if type(statement.get("Description")) != str:
        statement["Description"] = str(statement["Description"])
    if type(statement.get("Date")) != str:
        statement["Date"] = str(statement["Date"])
    if type(statement.get("Type")) != str:
        statement["Type"] = str(statement["Type"])

    try:
        if type(statement.get("Amount")) != float:
            statement["Amount"] = float(statement["Amount"])
    except (ValueError, TypeError):
        return f"Cannot convert Amount {statement.get('Amount')!r} to float"

    try:
        if type(statement.get("Balance")) != float:
            statement["Balance"] = float(statement["Balance"])
    except (ValueError, TypeError):
        return f"Cannot convert Balance {statement.get('Balance')!r} to float"

    return None


def validate(statement):
    """Check that a normalized statement's fields are well-formed.

    Returns None if valid, or an error message string describing the first
    failure found.
    """
    if type(statement["Acct_NO"]) != str:
        return "Acct_NO is not a string"
    if type(statement["Description"]) != str:
        return "Description is not a string"
    try:
        datetime.strptime(statement["Date"], "%m/%d/%y")
    except ValueError:
        return f"Date {statement['Date']!r} is not in MM/DD/YY format"
    if statement["Type"] not in ("Credit", "Debit"):
        return f"Type {statement['Type']!r} is not 'Credit' or 'Debit'"
    if type(statement["Amount"]) != float:
        return "Amount is not a float"
    if type(statement["Balance"]) != float:
        return "Balance is not a float"
    return None
