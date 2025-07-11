#!/usr/bin/env python3
"""
Test script to isolate the template rendering error
"""

import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from config.settings import DevelopmentConfig
from app.models.user import CalendarNote, User
from flask import render_template, render_template_string
from datetime import date

def test_day_template():
    """Test rendering the day template to isolate the error"""
    app = create_app()
    app.config.from_object(DevelopmentConfig)
    
    with app.app_context():
        # Login as admin (simulate login context)
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            print("Admin user not found")
            return
            
        # Get notes for 2025-07-12
        target_date = date(2025, 7, 12)
        notes = CalendarNote.query.filter(
            CalendarNote.date_for == target_date
        ).order_by(CalendarNote.created_at.desc()).all()
        
        print(f"Found {len(notes)} notes for {target_date}")
        
        # Test each note individually
        for i, note in enumerate(notes):
            print(f"\nTesting note {i+1}:")
            print(f"  ID: {note.id}")
            print(f"  Title: {note.title}")
            print(f"  Created by: {note.created_by}")
            try:
                print(f"  Creator: {note.creator.username if note.creator else 'None'}")
            except Exception as e:
                print(f"  Creator error: {e}")
                
            try:
                print(f"  Reminder time: {note.reminder_time}")
            except Exception as e:
                print(f"  Reminder time error: {e}")
        
        # Try to render a simple template with notes
        simple_template = '''
        {% for note in notes %}
        <div>{{ note.title }} - {{ note.creator.username if note.creator else 'No creator' }}</div>
        {% endfor %}
        '''
        
        try:
            from flask_login import current_user
            # Mock current_user for template context
            with app.test_request_context():
                result = render_template_string(simple_template, notes=notes)
                print(f"\nSimple template rendered successfully!")
        except Exception as e:
            print(f"\nSimple template error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    test_day_template()
