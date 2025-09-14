#!/usr/bin/env python3

import json
from data_preprocessing import UserPermissions

# Load financial data
with open('full_financial_data.json', 'r') as f:
    financial_data = json.load(f)

# Test with full permissions
full_permissions = UserPermissions(
    assets=True,
    liabilities=True,
    transactions=True,
    epf_retirement_balance=True,
    credit_score=True,
    investments=True
)

print("=== FULL PERMISSIONS TEST ===")
masked_data = full_permissions.mask_data(financial_data)
print("Masked data with full permissions:")
print(json.dumps(masked_data, indent=2))

# Test with restricted permissions (only credit score)
restricted_permissions = UserPermissions(
    assets=False,
    liabilities=False,
    transactions=False,
    epf_retirement_balance=False,
    credit_score=True,
    investments=False
)

print("\n=== RESTRICTED PERMISSIONS TEST ===")
masked_data = restricted_permissions.mask_data(financial_data)
print("Masked data with restricted permissions (only credit score):")
print(json.dumps(masked_data, indent=2))

# Test with partial permissions
partial_permissions = UserPermissions(
    assets=True,
    liabilities=True,
    transactions=True,
    epf_retirement_balance=False,
    credit_score=False,
    investments=True
)

print("\n=== PARTIAL PERMISSIONS TEST ===")
masked_data = partial_permissions.mask_data(financial_data)
print("Masked data with partial permissions (assets, liabilities, transactions, investments):")
print(json.dumps(masked_data, indent=2))