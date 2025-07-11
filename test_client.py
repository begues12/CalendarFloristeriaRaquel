#!/usr/bin/env python3
"""
Test script using Flask test client to replicate the web request context
"""

import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from config.settings import DevelopmentConfig

def test_with_client():
    """Test using Flask test client to replicate the exact web request"""
    app = create_app()
    app.config.from_object(DevelopmentConfig)
    
    with app.test_client() as client:
        # Login
        login_response = client.post('/auth/login', data={
            'username': 'admin',
            'password': 'admin123'
        }, follow_redirects=False)
        
        print(f"Login response status: {login_response.status_code}")
        
        # Try to access the day view that was causing the 500 error
        day_response = client.get('/day/2025-07-12')
        print(f"Day view response status: {day_response.status_code}")
        
        if day_response.status_code == 500:
            print("500 Error content:")
            print(day_response.get_data(as_text=True)[:1000])
        elif day_response.status_code == 200:
            print("Day view rendered successfully!")
            if 'created_by_user' in day_response.get_data(as_text=True):
                print("Found 'created_by_user' in response!")
        else:
            print(f"Unexpected status code: {day_response.status_code}")

if __name__ == '__main__':
    test_with_client()
