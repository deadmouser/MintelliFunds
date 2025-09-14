#!/usr/bin/env python3

import sqlite3
from datetime import datetime, timedelta

# Connect to the privacy database
conn = sqlite3.connect('production_privacy.db')
cursor = conn.cursor()

# Create consent records for test_user_123 for all categories
user_id = "test_user_123"
categories = [
    "assets",
    "liabilities", 
    "transactions",
    "epf_retirement_balance",
    "credit_score",
    "investments"
]

# Insert consent records
for category in categories:
    cursor.execute('''
        INSERT INTO consent_records 
        (user_id, category, permission_level, granted_at, expires_at, purpose)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (
        user_id,
        category,
        "full_access",
        datetime.now().isoformat(),
        (datetime.now() + timedelta(days=365)).isoformat(),
        "financial_analysis"
    ))

conn.commit()
conn.close()

print("Consent records created for user test_user_123")