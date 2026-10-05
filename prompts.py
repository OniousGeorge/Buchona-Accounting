import json

#with open(db.DATA_DIR / "train_labeled.json") as f:
  #  train_labeled = json.load(f)

CATEGORY_PARENTS = {
    "Insurance": "Bills",
    "Rent": "Bills",
    "Water": "Bills",
    "Subscription": "Bills",
    "Internet": "Bills",
    "Groceries": "Food",
    "Eating Out": "Food",
    "Gas": "Self Transportation",
    "Consumer Spending": "Consumer Spending",
    "Deposit": "Income",
    "Cash Back" : "Money Received",
    "Misc" : "Misc",
    "Credit Card Payment":"Bills",
    "Savings": "Transfer",
    "Car Maintenance": "Self Transportation",
    "Transportation": "Misc",
    "Entertainment": "Consumer Spending",
    "Fines": "Bills",
    "Transfer": "Transfer",
    "Interest Charge": "Misc",
    "Refund": "Money Received",
    "Zelle Sent": "Money Sent",
    "Venmo Sent": "Money Sent",
    "Cash App Sent": "Money Sent",
    "Apple Cash Sent": "Money Sent",
    "Zelle Received": "Money Received",
    "Venmo Received": "Money Received",
    "Cash App Received": "Money Received",
    "Apple Cash Received": "Money Received",
    "Uncategorized": "Uncategorized",
}

child_cat=sorted(c for c in CATEGORY_PARENTS if c != "Uncategorized")

SYSTEM_PROMPT=("Your job is to categorize personal bank transactions. "  
               "Reply with only one category from this list and nothing else: " + ", ".join(child_cat))


def format_trans(description, amount):
    return f"Description: {description}\nAmount: {amount:.2f}"

def build_prompt_messages(description, amount):
    return[{"role": "system", "content": SYSTEM_PROMPT},
           {"role": "user", "content": format_trans(description, amount)}]

def training_example(item):
    if item["category"] not in child_cat:
        raise ValueError(f"Invalid label {item['category']!r} for {item['description']!r}")
    return{"prompt":build_prompt_messages(item["description"], item["amount"]),
           "completion": [{"role": "assistant", "content": item["category"]}], }
if __name__ == "__main__":
    import pprint

    good = {"description": "WAWA 8142", "amount": -10.99, "account": "credit",
            "date": "08/09/26", "category": "Eating Out"}
    pprint.pprint(training_example(good))

