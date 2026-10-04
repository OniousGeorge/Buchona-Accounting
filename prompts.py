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
    "Gas": "Transportation",
    "Consumer Spending": "Shopping",
    "Deposit": "Income",
    "Cash Back" : "Income",
    "Misc" : "Misc",
    "Credit Card Payment":"Bills",
    "Savings": "Savings",
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

