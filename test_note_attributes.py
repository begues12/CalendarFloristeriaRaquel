#!/usr/bin/env python3
"""
Test script to reproduce the CalendarNote error
"""

import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.models.user import CalendarNote, User
from flask import render_template_string

def test_note_attributes():
    """Test CalendarNote attributes to see what's available"""
    from config.settings import DevelopmentConfig
    app = create_app()
    app.config.from_object(DevelopmentConfig)
    
    with app.app_context():
        # Get a sample note
        note = CalendarNote.query.first()
        if note:
            print("CalendarNote attributes:")
            for attr in dir(note):
                if not attr.startswith('_'):
                    try:
                        value = getattr(note, attr)
                        print(f"  {attr}: {value}")
                    except Exception as e:
                        print(f"  {attr}: Error - {e}")
            
            # Test template rendering with note
            template = """
            <div>
                Note: {{ note.title }}
                Creator: {{ note.creator.username if note.creator else 'No creator' }}
                Created by: {{ note.created_by }}
            </div>
            """
            
            try:
                result = render_template_string(template, note=note)
                print("\nTemplate rendering successful:")
                print(result)
            except Exception as e:
                print(f"\nTemplate rendering error: {e}")
        else:
            print("No CalendarNote found in database")

if __name__ == '__main__':
    test_note_attributes()
