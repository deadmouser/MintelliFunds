#!/usr/bin/env python3

import sqlite3
from datetime import datetime

# Connect to the privacy database
conn = sqlite3.connect('production_privacy.db')
cursor = conn.cursor()

# Revoke access to some categories for test_user_123
user_id = "test_user_123"
categories_to_revoke = ["credit_score", "investments"]

# Update consent records to revoke access
for category in categories_to_revoke:
    cursor.execute('''
        UPDATE consent_records 
        SET revoked = ?, revoked_at = ?
        WHERE user_id = ? AND category = ?
    ''', (
        True,
        datetime.now().isoformat(),
        user_id,
        category
    ))

conn.commit()
conn.close()

print("Revoked access to credit_score and investments for user test_user_123")