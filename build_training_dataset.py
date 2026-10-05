import db
import json
from prompts import CATEGORY_PARENTS

transactions = db.list_all()

training = transactions[:598]
eval_set = transactions[598:]

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
    "WM SUPERC": "Groceries",
    "FAMILY DOLLAR": "Groceries",
    "BIG LOTS": "Groceries",
    "WAWA": "Eating Out",
    "365 MARKET": "Eating Out",
    "DOORDASH": "Eating Out",
    "AMERICAN WATER WORKS": "Water",
    "JOHN GATTO": "Rent",
    # Payment apps. categorize() adds " Sent" or " Received" from the amount's
    # sign. Keep these BELOW "JOHN GATTO" so the landlord's Zelle stays Rent.
    "ZELLE": "Zelle",
    "VENMO": "Venmo",
    "CASH APP": "Cash App",
    "APPLE CASH": "Apple Cash",
    "TJMAXX": "Consumer Spending",
    "EXXONMOBIL": "Gas",
    # Above "INTEREST" on purpose: a card interest charge is money out.
    "INTEREST CHARGE": "Interest Charge",
    "INTEREST": "Cash Back",
    "CAPITAL ONE MOBILE PMT": "Credit Card Payment",
    "CAPITAL ONE MOBILE PYMT": "Credit Card Payment",
    "GRIL" : "Eating Out",
    "Netflix" : "Subscription",
    "PLANET FIT": "Subscription",
    "AMAZON WEB SERVICES": "Subscription",
    "COMCAST": "Internet",
    "BURGER KING": "Eating Out",
    "WAFFLE HOUSE": "Eating Out",
    "ATERA519": "Eating Out",
    "SHEETZ": "Eating Out",
    "CITGO": "Gas",
    "WAL-MART": "Groceries",
    "360 PERFORMANCE SAVINGS": "Savings",
    "ROOT INSURANCE": "Insurance",

    # Gas
    "SUNOCO": "Gas",
    "KWIK MART": "Gas",
    "GULF OIL": "Gas",
    "PILOT": "Gas",
    "CIRCLEK": "Gas",
    "FILL & FLY": "Gas",

    # Eating Out
    "TACO BELL": "Eating Out",
    "GRUBHUB": "Eating Out",
    "DAIRY QUEEN": "Eating Out",
    "DOMINO S": "Eating Out",
    "YUMMY BOWL": "Eating Out",
    "MCDONALD": "Eating Out",
    "OLIVE GARDEN": "Eating Out",
    "UBER EATS": "Eating Out",
    "CINNABON": "Eating Out",
    "PIZZA HUT": "Eating Out",
    "SHAKE SHACK": "Eating Out",
    "NARDOZZI": "Eating Out",
    "BERLEW": "Eating Out",
    "NOTIS THE GYRO": "Eating Out",
    "XAVIS": "Eating Out",
    "ARBYS": "Eating Out",
    "DAVES HOT CHICKEN": "Eating Out",
    "DUNKIN": "Eating Out",
    "EL RANCHERO": "Eating Out",
    "FLAMEHOUSE": "Eating Out",
    "GIOS PIZZA": "Eating Out",
    "HURRICANE HOLE": "Eating Out",
    "IHOP": "Eating Out",
    "MOE S": "Eating Out",
    "NEW CHINA STAR": "Eating Out",
    "PANDARELLA": "Eating Out",
    "WENDYS": "Eating Out",
    "A S EATERY": "Eating Out",
    "PRIMOHOAIGES": "Eating Out",
    "BUCKTOWN DINER": "Eating Out",
    "JITTY JOE": "Eating Out",
    "BUBBAKOO": "Eating Out",
    "BURRITO LOCO": "Eating Out",
    "LOTUS TEA": "Eating Out",
    "BARTARI": "Eating Out",
    "SCRANTON KIOSKS": "Eating Out",
    "GEORGE VENDING": "Eating Out",

    # Groceries
    "WEIS MARKETS": "Groceries",
    "MARKET32": "Groceries",
    "WALMART": "Groceries",
    "WAL MART": "Groceries",
    "VALLEY SUPERMARKET": "Groceries",
    "GIANT": "Groceries",
    "WEGMANS": "Groceries",

    # Consumer Spending
    "TARGET": "Consumer Spending",
    "MERCARI": "Consumer Spending",
    "OLD NAVY": "Consumer Spending",
    "FIVE BELOW": "Consumer Spending",
    "SHEIN": "Consumer Spending",
    "HOME DEPOT": "Consumer Spending",
    "ADIDAS": "Consumer Spending",
    "AMAZON MARK": "Consumer Spending",
    "AMAZON RETA": "Consumer Spending",
    "BARNES NOBLE": "Consumer Spending",
    "BATH & BODY": "Consumer Spending",
    "DICKS SPORTING": "Consumer Spending",
    "HOUSE OF SPORTS": "Consumer Spending",
    "JD 1055": "Consumer Spending",
    "MICHAELS": "Consumer Spending",
    "OLLIES": "Consumer Spending",
    "P AND R DISCOUNT": "Consumer Spending",
    "POKE A NOSE": "Consumer Spending",
    "REI COM": "Consumer Spending",
    "SALLY BEAUTY": "Consumer Spending",
    "SEASHELLS": "Consumer Spending",
    "BILLIONAIRE BOYS": "Consumer Spending",
    "ISLAND GIFTS": "Consumer Spending",
    "TIKTOK SHOP": "Consumer Spending",
    "VARIETY WHOLESALERS": "Consumer Spending",
    "GNC": "Consumer Spending",

    # After SEASHELLS on purpose: "SEASHELLS" contains "SHELL", and first match wins.
    "SHELL": "Gas",

    "CVS": "Groceries",
    "COSMOS": "Eating Out",
    "JACK S FOOD MART": "Eating Out",
    "AUTOZONE": "Car Maintenance",
    "MAVIS": "Car Maintenance",
    # After "UBER EATS" on purpose: plain UBER is a ride, UBER EATS is food.
    "UBER": "Transportation",
    "SNYDERSVILLE GOLF": "Entertainment",
    "CANOPY TOU": "Entertainment",
    "ZAISU": "Entertainment",
    "CENGAGE": "Misc",
    "PLAYSTATION": "Subscription",
    "SPEECHIFY": "Subscription",
    "PA COURTS": "Fines",
    "WELLS FARGO": "Transfer",
    "DISCOVER E-PAYMENT": "Credit Card Payment",
    "CASH BACK REWARD": "Cash Back",
    # American Airlines: ticket numbers start with 001. Not plain "AMERICAN",
    # which would also match other merchants (e.g. AMERICAN WATER WORKS).
    "AMERICAN  001": "Transportation",
    "SPIRIT AI": "Misc",

    # Money moving between my own accounts.
    "360 CHECKING": "Transfer",
    "SOFI": "Transfer",
    "INSTANT TRANSFER RECEIVED FROM ONIOUS": "Transfer",

    # Last on purpose: "Deposit from ..." also appears on transfers and app
    # cash-outs, so every more specific keyword above must get the first chance.
    "DEPOSIT": "Deposit",
}

# Payment-app labels that get a direction added in categorize().
PAYMENT_APPS = {"Zelle", "Venmo", "Cash App", "Apple Cash"}

# Parents whose categories are purchases. Money coming IN on one of these is a
# refund. (A card payment is under Bills but is not a purchase, so it is skipped.)
PURCHASE_PARENTS = {"Food", "Consumer Spending", "Self Transportation", "Bills"}

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

        # Same app, opposite directions: the sign says which one this row is.
        if category in PAYMENT_APPS:
            category += " Sent" if amount < 0 else " Received"
        # A purchase with a positive amount is the store giving money back.
        elif (amount > 0 and category != "Credit Card Payment"
              and CATEGORY_PARENTS[category] in PURCHASE_PARENTS):
            category = "Refund"

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
with open(db.TRAIN_DATASET_PATH, "w") as f:
    json.dump(train_labeled, f, indent=2)
with open(db.EVAL_DATASET_PATH, "w") as f:
    json.dump(eval_labeled, f, indent=2)

print_summary("Training", train_summary)
print_summary("Eval", eval_summary)

print(f"\nSaved {len(train_labeled)} transactions to {db.TRAIN_DATASET_PATH.name}")
print(f"Saved {len(eval_labeled)} transactions to {db.EVAL_DATASET_PATH.name}")


