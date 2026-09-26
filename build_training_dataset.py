import db
import json

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
    "PERSON A": "Rent",
    "VENMO": "Misc",
    "CASH APP": "Misc",
    "TJMAXX": "Consumer Spending",
    "EXXONMOBIL": "Gas",
    "CAPITAL ONE": "Credit Card",
    "WITHDRAWAL": "Financial",
    "INTEREST": "Misc",
}

# The model only ever predicts the child category; the parent is looked up here.
CATEGORY_PARENTS = {
    "Insurance": "Bills",
    "Rent": "Bills",
    "Water": "Bills",
    "Credit Card": "Bills",
    "Groceries": "Food",
    "Eating Out": "Food",
    "Gas": "Transportation",
    "Consumer Spending": "Shopping",
    "Deposit": "Income",
    "Financial": "Financial",
    "Misc": "Misc",
}

# Auto-categorize training transactions
categorized = []
summary = {}

print("Auto-categorizing training transactions:\n")

for idx, txn in enumerate(training, 1):
    _, _, description, _, txn_type, amount, _ = txn

    category = "Uncategorized"
    for keyword, cat in categorize_key_words.items():
        if keyword.upper() in description.upper():
            category = cat
            break

    categorized.append({
        "description": description,
        "amount": amount,
        "type": txn_type,
        "category": category
    })

    summary[category] = summary.get(category, 0) + 1
    print(f"{idx}. [{category}] {description} - ${amount}")

# Save to file
with open(db.DATA_DIR / "training_data.json", "w") as f:
    json.dump(categorized, f, indent=2)

print("\n" + "=" * 80)
print("Category summary (parent > child):")
for cat in sorted(summary, key=lambda c: (CATEGORY_PARENTS[c], c)):
    print(f"  {CATEGORY_PARENTS[cat]} > {cat}: {summary[cat]}")

print(f"\n✓ Saved {len(categorized)} transactions to data/training_data.json")