#!/usr/bin/env python3
"""
Quick user check
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.models.user import User

app = create_app()
with app.app_context():
    users = User.query.all()
    print("Current users:")
    for u in users:
        print(f"ID: {u.id}, Username: {u.username}, Email: {u.email}")
