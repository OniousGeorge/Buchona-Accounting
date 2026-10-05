"""Type coercion and validation for a single transaction dict.

Migrated from csv.ipynb. The original functions printed an error and
returned False on failure, so the reason a row failed only ever reached the
console. These now return None on success, or an error message string
describing exactly what failed, so a caller (pipeline.py, later) can decide
what to do with that message instead of it being forced to stdout.
"""
from datetime import datetime

# Dates are stored as ISO text (e.g. 2026-09-06): year first, zero-padded, so
# sorting the text also sorts by date, across years.
ISO_DATE = "%Y-%m-%d"


def date_error(date):
    """Return None if date is a zero-padded YYYY-MM-DD string, else an error message."""
    try:
        parsed = datetime.strptime(date, ISO_DATE)
    except ValueError:
        return f"Date {date!r} is not in YYYY-MM-DD format"
    if parsed.strftime(ISO_DATE) != date:
        return f"Date {date!r} is not zero-padded YYYY-MM-DD"
    return None


def debit_normalize(statement):
    """Coerce fields to their expected types, in place.

    Returns None on success, or an error message string on failure.
    """
    if type(statement.get("Description")) != str:
        statement["Description"] = str(statement["Description"])
    if type(statement.get("Date")) != str:
        statement["Date"] = str(statement["Date"])

    # The checking CSV uses MM/DD/YY; store ISO YYYY-MM-DD so text sorts by date.
    try:
        statement["Date"] = datetime.strptime(statement["Date"], "%m/%d/%y").strftime(ISO_DATE)
    except ValueError:
        return f"Cannot convert Date {statement['Date']!r} from MM/DD/YY"

    try:
        if type(statement.get("Amount")) != float:
            statement["Amount"] = float(statement["Amount"])
    except (ValueError, TypeError):
        return f"Cannot convert Amount {statement.get('Amount')!r} to float"

    try:
        if type(statement.get("Balance")) != float:
            statement["Balance"] = round(float(statement["Balance"]),2)
    except (ValueError, TypeError):
        return f"Cannot convert Balance {statement.get('Balance')!r} to float"

    return None

def credit_normalize(statement):
    """Coerce fields to their expected types, in place.

    Returns None on success, or an error message string on failure.
    """
    if type(statement.get("Description")) != str:
        statement["Description"] = str(statement["Description"])
    if type(statement.get("Date")) != str:
        statement["Date"] = str(statement["Date"])
    if type(statement.get("Category")) != str:
        statement["Category"] = str(statement["Category"])

    # The card CSV is already YYYY-MM-DD; re-format it so it is zero-padded.
    try:
        statement["Date"] = datetime.strptime(statement["Date"], ISO_DATE).strftime(ISO_DATE)
    except ValueError:
        return f"Cannot read Date {statement['Date']!r} as YYYY-MM-DD"

    try:
        if type(statement.get("Amount")) != float:
            statement["Amount"] = round(float(statement["Amount"]), 2)
    except (ValueError, TypeError):
        return f"Cannot convert Amount {statement.get('Amount')!r} to float"

    return None

def debit_validate(statement):
    """Check that a normalized statement's fields are well-formed.

    Returns None if valid, or an error message string describing the first
    failure found.
    """
    if type(statement["Description"]) != str:
        return "Description is not a string"
    error = date_error(statement["Date"])
    if error is not None:
        return error
    if type(statement["Amount"]) != float:
        return "Amount is not a float"
    if type(statement["Balance"]) != float:
        return "Balance is not a float"
    return None

def credit_validate(statement):
    """Check that a normalized statement's fields are well-formed.

    Returns None if valid, or an error message string describing the first
    failure found.
    """
    if type(statement["Description"]) != str:
        return "Description is not a string"
    if type(statement["Category"]) != str:
        return "Category is not a string"
    error = date_error(statement["Date"])
    if error is not None:
        return error
    if type(statement["Amount"]) != float:
        return "Amount is not a float"
    return None
