import json
import random

random.seed(42)

def credit_rating(score: int) -> str:
    if score >= 750: return "Excellent"
    if score >= 700: return "Good"
    if score >= 650: return "Fair"
    if score >= 600: return "Average"
    return "Poor"

def gen_monthly_income(age: int) -> int:
    if age < 30:
        return random.randint(25000, 80000)
    elif age < 40:
        return random.randint(50000, 150000)
    elif age < 50:
        return random.randint(80000, 300000)
    else:
        return random.randint(60000, 200000)

def gen_record() -> dict:
    # Demographics used only for realism in calculations (not returned)
    age = random.randint(22, 65)

    # Income and spending realism (INR, monthly)
    monthly_income = gen_monthly_income(age)
    monthly_expenses = int(monthly_income * random.uniform(0.62, 0.86))
    monthly_transfers = int(monthly_income * random.uniform(0.01, 0.08))

    # Assets
    # Cash is small-liquid, bank_balances is larger liquid; property can be 0 if rented
    cash = random.randint(3000, 80000)
    # Bank balances roughly 0.5–6 months of income with randomness
    bank_balances = int(random.uniform(0.5, 6.0) * monthly_income * random.uniform(0.6, 1.4))
    # Property ownership ~40%; value distribution approximated for Indian cities (no city field returned)
    if random.random() < 0.40:
        # Metro/non-metro like spread
        tier = random.choices(["metro", "tier1", "tier2"], weights=[0.35, 0.4, 0.25])[0]
        if tier == "metro":
            property_value = random.randint(6000000, 40000000)
        elif tier == "tier1":
            property_value = random.randint(3500000, 22000000)
        else:
            property_value = random.randint(2000000, 14000000)
    else:
        property_value = 0

    # Liabilities
    loans = 0
    if property_value > 0 and random.random() < 0.7:
        # Outstanding portion of a typical home loan
        loans = random.randint(int(property_value * 0.25), int(property_value * 0.65))
    # Add possibility of personal/car loan if no home loan or to stack small amounts
    if loans == 0 and random.random() < 0.25:
        loans += random.randint(50000, 500000)
    credit_card_debt = random.randint(0, 150000) if random.random() < 0.38 else 0

    # EPF (12% employee + employer; INR 1,800 cap each)
    employee_contribution = min(int(monthly_income * 0.12), 1800)
    employer_match = employee_contribution
    # Estimate current balance by simulating years of service (0–35) and growth band
    years_service = max(0, min(age - 22, 35))
    epf_current_balance = int((employee_contribution + employer_match) * 12 * years_service * random.uniform(1.10, 1.70))

    # Credit Score (300–900) influenced by income and debt load
    base = 650
    dti = (loans + credit_card_debt) / max(monthly_income, 1)
    if dti > 25: base -= random.randint(30, 120)
    if monthly_income > 100000: base += random.randint(30, 90)
    if age > 35: base += random.randint(15, 45)
    score = max(300, min(900, base + random.randint(-90, 90)))
    rating = credit_rating(score)

    # Investments: totals only by class; bounded by plausible savings/investor behavior
    # Allocate a fraction of monthly savings into totals (no names, no instruments)
    monthly_savings = max(0, monthly_income - monthly_expenses)
    # Simulate investment accumulation horizon without exposing years
    accumulation_factor = random.uniform(6, 48)  # months-equivalent
    invest_total_budget = int(monthly_savings * accumulation_factor * random.uniform(0.4, 0.9))
    if invest_total_budget == 0 and random.random() < 0.15:
        invest_total_budget = random.randint(10000, 80000)

    # Split into stocks, mutual funds, bonds (totals only)
    if invest_total_budget > 0:
        w1 = random.uniform(0.2, 0.6)   # stocks
        w2 = random.uniform(0.2, 0.6)   # mutual funds
        w3 = max(0.0, 1.0 - (w1 + w2))  # bonds
        # Normalize if w1+w2>1
        s = w1 + w2 + w3
        w1, w2, w3 = w1/s, w2/s, w3/s
        stocks_amt = int(invest_total_budget * w1)
        mutual_funds_amt = int(invest_total_budget * w2)
        bonds_amt = invest_total_budget - stocks_amt - mutual_funds_amt
    else:
        stocks_amt = mutual_funds_amt = bonds_amt = 0

    # Build the exact required shape, with readable field names and no extras
    return {
        "assets": {
            "cash": int(cash),
            "bank_balances": int(bank_balances),
            "property": int(property_value)
        },
        "liabilities": {
            "loans": int(loans),
            "credit_card_debt": int(credit_card_debt)
        },
        "transactions": {
            "income": int(monthly_income),
            "expenses": int(monthly_expenses),
            "transfers": int(monthly_transfers)
        },
        "epf_retirement_balance": {
            "contributions": int(employee_contribution),
            "employer_match": int(employer_match),
            "current_balance": int(epf_current_balance)
        },
        "credit_score": {
            "score": int(score),
            "rating": rating
        },
        "investments": {
            "stocks": int(stocks_amt),
            "mutual_funds": int(mutual_funds_amt),
            "bonds": int(bonds_amt)
        }
    }

def generate_dataset(n_users: int = 20000):
    for _ in range(n_users):
        yield gen_record()

if __name__ == "__main__":
    # Choose 10000–20000 as needed
    N = 20000
    out_file = "indian_financial_min_fields.json"

    # Minified JSON (no spaces) to keep file size small while preserving field names
    data = list(generate_dataset(N))
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, separators=(",", ":"))

    # Quick size estimate (rough)
    import os
    size_mb = os.path.getsize(out_file) / (1024 * 1024)
    print(f"Saved {N} users to {out_file} ({size_mb:.2f} MB)")
