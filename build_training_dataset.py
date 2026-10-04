import db
import json
from prompts import CATEGORY_PARENTS

transactions = db.list_all()

training = transactions[:38]
eval_set = transactions[38:]

print(f"number of transactions: {len(transactions)}")
print(f"number of training transactions: {len(training)}")
print(f"number of eval transactions: {len(eval_set)}")
print("=" * 80 + "\n")
for s in transactions:
    print(s)
print("=" * 80 + "\n")


categorize_key_words = {
    "GEICO": "Insurance",
    "ALDI": "Groceries",
    "DOLLAR GENERAL": "Groceries",
    "WM SUPERCENTER": "Groceries",
    "FAMILY DOLLAR": "Groceries",
    "BIG LOTS": "Groceries",
    "WAWA": "Eating Out",
    "365 MARKET": "Eating Out",
    "DOORDASH": "Eating Out",
    "DEPOSIT": "Deposit",
    "APPLE CASH": "Deposit",
    "AMERICAN WATER WORKS": "Water",
    "JOHN GATTO": "Rent",
    "VENMO": "Misc",
    "CASH APP": "Misc",
    "TJMAXX": "Consumer Spending",
    "EXXONMOBIL": "Gas",
    "INTEREST": "Cash Back",
    "CAPITAL ONE MOBILE PMT": "Credit Card Payment",
    "CAPITAL ONE MOBILE PYMT": "Credit Card Payment",
    "GRIL" : "Eating Out",
    "Netflix" : "Subscription",
    "PLANET FITNESS": "Subscription",
    "AMAZON WEB SERVICES": "Subscription",
    "COMCAST": "Internet",
    "BURGER KING": "Eating Out",
    "WAFFLE HOUSE": "Eating Out",
    "ATERA519": "Eating Out",
    "SHEETZ": "Eating Out",
    "CITGO": "Gas",
    "WAL-MART": "Groceries",
    "360 PERFORMANCE SAVINGS": "Savings",
}

# The model only ever predicts the child category; the parent is looked up here.


def categorize(rows):
    """Keyword-label each (account, description, date, amount) row.

    Returns (categorized, summary): a list of labeled dicts, and a dict of
    category -> number of rows that got it.
    """
    categorized = []
    summary = {}

    for idx, txn in enumerate(rows, 1):
        account, description, date, amount = txn

        category = "Uncategorized"
        for keyword, cat in categorize_key_words.items():
            if keyword.upper() in description.upper():
                category = cat
                break

        categorized.append({
            "description": description,
            "amount": amount,
            "account": account,
            "date" : date,
            "category": category
        })

        summary[category] = summary.get(category, 0) + 1
        print(f"{idx}. [{category}] {description} - ${amount}")

    return categorized, summary


def print_summary(title, summary):
    print("\n" + "=" * 80)
    print(f"{title} category summary (parent > child):")
    for cat in sorted(summary, key=lambda c: (CATEGORY_PARENTS[c], c)):
        print(f"  {CATEGORY_PARENTS[cat]} > {cat}: {summary[cat]}")


print("Auto-categorizing training transactions:\n")
train_labeled, train_summary = categorize(training)

print("\nAuto-categorizing eval transactions:\n")
eval_labeled, eval_summary = categorize(eval_set)

# Each split gets its own file so eval labels can never leak into training.
with open(db.DATA_DIR / "train_labeled.json", "w") as f:
    json.dump(train_labeled, f, indent=2)
with open(db.DATA_DIR / "eval_labeled.json", "w") as f:
    json.dump(eval_labeled, f, indent=2)

print_summary("Training", train_summary)
print_summary("Eval", eval_summary)

print(f"\nSaved {len(train_labeled)} transactions to data/train_labeled.json")
print(f"Saved {len(eval_labeled)} transactions to data/eval_labeled.json")
